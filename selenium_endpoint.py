import os
import random
import re
import shutil
import string
import time
import uuid
import requests
from flask import Blueprint, jsonify, request
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

TEMPORARY_DOWNLOAD_FOLDER = r"C:\auto_youtube\temp\\"
ACTIVE_SELENIUM_INSTANCES = {}
BASE_FOLDER_YOUTUBE_AUTOMATIONS_PATH = r"C:\auto_youtube\\"
selenium_bp = Blueprint('selenium_bp', __name__)


@selenium_bp.route('/start_selenium', methods=['POST'])
def start_selenium():
    """Start a new Selenium instance and return an instance_id."""
    opts = uc.ChromeOptions()
    opts = uc.ChromeOptions()
    opts.add_argument("--lang=en")
    opts.page_load_strategy = 'none'
    # opts.add_argument("--headless")
    opts.add_argument(r"--user-data-dir=C:\Users\space\AppData\Local\Google\Chrome\User Data")
    opts.add_argument("--profile-directory=Default")
    driver = uc.Chrome(options=opts, browser_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")

    # Create a unique ID for this session
    instance_id = str(uuid.uuid4())

    # Store the driver in the dictionary
    ACTIVE_SELENIUM_INSTANCES[instance_id] = driver

    return jsonify({"instance_id": instance_id}), 200


@selenium_bp.route('/goto_url/<instance_id>', methods=['POST'])
def goto_url(instance_id):
    """Navigate the browser for a given Selenium instance."""
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        return jsonify({"error": "Invalid instance_id"}), 404

    driver.get(url)
    return jsonify({"status": f"Navigated to {url}"}), 200


@selenium_bp.route('/get_title/<instance_id>', methods=['GET'])
def get_title(instance_id):
    """Return the current page title for the given instance."""
    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        return jsonify({"error": "Invalid instance_id"}), 404

    title = driver.title
    return jsonify({"title": title}), 200


@selenium_bp.route('/close_selenium/<instance_id>', methods=['POST'])
def close_selenium(instance_id):
    """Quit the Selenium instance and remove it from the dictionary."""
    driver = ACTIVE_SELENIUM_INSTANCES.pop(instance_id, None)
    if driver is None:
        return jsonify({"error": "Instance not found"}), 404

    driver.quit()
    return jsonify({"status": "Closed Selenium instance"}), 200


#######################################################
#######################################################
#################### OPUS PRO #########################
#######################################################
#######################################################

def move_file_to_target(video_id, clip_id, category, file_name=None):
    """
    Moves the first file in the temporary download folder to the target folder structure.

    :param video_id: The ID of the parent video
    :param clip_id: The ID of the clip
    :param category: The category of the file
    :param file_name: Optional new name for the file in the target folder
    :return: JSON response indicating success or failure
    """
    # Ensure the temporary download folder exists
    if not os.path.exists(TEMPORARY_DOWNLOAD_FOLDER):
        return None

    # Get the first file in the temporary download folder
    temp_files = os.listdir(TEMPORARY_DOWNLOAD_FOLDER)
    if not temp_files:
        return None

    # Select the first file
    temp_file = temp_files[0]
    print(f'file name {temp_file}')
    temp_file_path = os.path.join(TEMPORARY_DOWNLOAD_FOLDER, temp_file)

    # Ensure the temporary file exists
    if not os.path.isfile(temp_file_path):
        return None

    # Define the target folder and file path
    target_folder = os.path.join(BASE_FOLDER_YOUTUBE_AUTOMATIONS_PATH, category, video_id, clip_id)
    os.makedirs(target_folder, exist_ok=True)  # Ensure the target folder exists

    # Use the provided file name or default to the original name
    target_file_name = file_name or temp_file
    target_file_path = os.path.join(target_folder, target_file_name)

    shutil.move(temp_file_path, target_file_path)



def process_video(
        parent_video_id: str,
        title: str,
        captions: str,
        clip_id: str,
        clip_number: int,
        category: str
):
    """
    Downloads a video from `video_link` into the folder `/{parent_video_id}/{clip_id}/`.
    Saves the video file using the sanitized `title` + extension.
    Writes the `captions` to a text file named 'captions' in the same folder.

    :param parent_video_id: Parent folder ID or name.
    :param video_link: Direct link (URL) to the video file.
    :param title: Title string to be used as the basis for the video file name.
    :param captions: Long string content to be saved to a text file.
    :param clip_id: Optional. If not provided, a random 12-character hash is generated.
    """

    # 1. Generate a clip_id if not provided
    if not clip_id:
        clip_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    # 2. Sanitize the title (remove special chars, replace spaces with '-')
    #    This pattern keeps letters, numbers, underscores, hyphens
    sanitized_title = re.sub(r'[^A-Za-z0-9_\-]+', '', title.replace(' ', '-'))

    # In case the title is empty or only has special chars after sanitizing,
    # give it a fallback name.
    if not sanitized_title:
        sanitized_title = "untitled"

    # 3. Create the folder structure: parent_video_id/clip_id
    folder_path = os.path.join(BASE_FOLDER_YOUTUBE_AUTOMATIONS_PATH, category, parent_video_id, f"{clip_id}_{str(clip_number)}")
    os.makedirs(folder_path, exist_ok=True)

    # 4. Download the video from `video_link` and save it
    #    We'll try to guess extension from the URL, or you can make it more robust
    #    by checking server headers or the content-type.
    #    For demonstration, we just grab whatever is after the last '.' in the URL or default to 'mp4'.

    # # Figure out possible extension
    # possible_ext = video_link.split('?')[0].split('.')[-1]
    # # If there's no "." found or the extension is suspiciously long, default to 'mp4'
    # extension = possible_ext if 1 <= len(possible_ext) <= 5 else "mp4"
    #
    # # Construct the video file path
    # video_filename = f"{sanitized_title}.{extension}"
    # video_path = os.path.join(folder_path, video_filename)
    #
    # # Download the video file
    # try:
    #     response = requests.get(video_link, stream=True)
    #     response.raise_for_status()  # Raise an error on invalid response
    #
    #     with open(video_path, 'wb') as f:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             if chunk:  # filter out keep-alive new chunks
    #                 f.write(chunk)
    # except Exception as e:
    #     print(f"Error downloading video: {e}")
    #     return  # or handle error as appropriate for your use-case




    # 5. Write the captions to a text file named "captions" in the same folder
    captions_path = os.path.join(folder_path, "captions.txt")
    with open(captions_path, 'w', encoding='utf-8') as caption_file:
        caption_file.write(captions)

    title_path = os.path.join(folder_path, "title.txt")
    with open(title_path, 'w', encoding='utf-8') as title_file:
        title_file.write(title)

    # Print out or return the folder/video paths if needed
    print(f"Video Title '{title}'")
    print(f"Captions saved to: {captions_path}")

    return {
        'captions_path': captions_path,
        "title_path": title_path,
        "clip_id": f"{clip_id}_{str(clip_number)}"
    }


def scroll_to_load_all(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"last height {last_height}")
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for new content to load
        time.sleep(pause_time)

        # Calculate new scroll height and compare with last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"new height {new_height}")
        if new_height == last_height:
            break  # Break the loop if no more content is loaded
        last_height = new_height


def scroll_to_trigger(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll incrementally to trigger loading
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(pause_time)

        # Trigger scroll event explicitly
        ActionChains(driver).scroll_by_amount(0, 1000).perform()

        # Check if new content has loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


@selenium_bp.route('/opuspro/submit_clipbasic/<instance_id>', methods=['POST'])
def submit_clipbasic(instance_id):
    """Navigate the browser for a given Selenium instance."""
    data = request.json
    video_url = data.get("video_url")
    short_length_selection = data.get("length_options").split(',')
    print(type(short_length_selection))
    # allowed_domains = ["youtube", "rumble"]
    if not video_url:
        return jsonify({"error": "No video_url provided"}), 400

    if not short_length_selection:
        return jsonify({"error": "No short_length_selection provided"}), 400

    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        return jsonify({"error": "Invalid instance_id"}), 404

    # Go to opuspro dashboard
    driver.get('https://clip.opus.pro/dashboard')

    ## Input Video Link
    video_link_input_box = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/input"))
    )
    video_link_input_box.send_keys(f'{video_url}')
    time.sleep(4)
    # Get Token Balance & Operation Cost and calculate if possible to operate.
    tokens_balance = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div/div[1]/div/div[3]/div/div/p"))
    )
    tokens_balance = tokens_balance.text
    print(tokens_balance)

    tokens_price = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div/div[1]/div[2]/div[4]/div[2]/div/div/p"))
    )
    tokens_price = tokens_price.text
    print(tokens_price)

    if int(tokens_balance) - int(tokens_price) < 0:
        return jsonify({
            "error": "You dont have enough tokens.",
            "balance": f"{tokens_balance}",
            "price": f"{tokens_price}"
        }), 400
    else:
        pass
    scroll_to_trigger(driver)
    scroll_to_trigger(driver)
    # OPEN LENGTH MENU
    clip_length_menu = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div[2]/button"))
    )
    clip_length_menu.click()
    time.sleep(10)
    # SELECT FIRST OPTION TO RESET SELECTION
    clip_length_menu_first_option = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[4]/div/div/div/div/div/div/div[1]"))
    )
    clip_length_menu_first_option.click()

    # SELECT LENGTH OPTIONS
    for i in short_length_selection:
        length_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 f"/html/body/div[4]/div/div/div/div/div/div/div[{i}]"))
        )
        length_option.click()

    # CLOSE MENU
    clip_length_menu.click()
    scroll_to_trigger(driver)
    scroll_to_trigger(driver)
    # my_templates_button CLICK
    my_templates_button = driver.find_element(By.XPATH,
                                              "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[2]/button")
    driver.execute_script("arguments[0].scrollIntoView();", my_templates_button)

    my_templates_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[2]/button"))
    )
    my_templates_button.click()

    return jsonify({
        "status": "done"
    }), 200

@selenium_bp.route('/opuspro/submit_clipanything/<instance_id>', methods=['POST'])
def submit_clipanything(instance_id):
    """Navigate the browser for a given Selenium instance."""
    data = request.json
    video_url = data.get("video_url")
    short_length_selection = data.get("length_options").split(',')
    print(type(short_length_selection))
    # allowed_domains = ["youtube", "rumble"]
    if not video_url:
        return jsonify({"error": "No video_url provided"}), 400

    if not short_length_selection:
        return jsonify({"error": "No short_length_selection provided"}), 400

    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        return jsonify({"error": "Invalid instance_id"}), 404

    # Go to opuspro dashboard
    driver.get('https://clip.opus.pro/dashboard')
    time.sleep(0.5)
    # Click on ClipAnything
    WebDriverWait(driver, timeout=20).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div[1]/div[1]/div/button[2]"))
    )

    ## Input Video Link
    video_link_input_box = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/input"))
    )
    video_link_input_box.send_keys(f'{video_url}')
    time.sleep(4)
    # Get Token Balance & Operation Cost and calculate if possible to operate.
    tokens_balance = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div/div[1]/div/div[3]/div/div/p"))
    )
    tokens_balance = tokens_balance.text
    print(tokens_balance)

    tokens_price = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div/div[1]/div[2]/div[4]/div[2]/div/div/p"))
    )
    tokens_price = tokens_price.text
    print(tokens_price)

    if int(tokens_balance) - int(tokens_price) < 0:
        return jsonify({
            "error": "You dont have enough tokens.",
            "balance": f"{tokens_balance}",
            "price": f"{tokens_price}"
        }), 400
    else:
        pass
    scroll_to_trigger(driver)
    scroll_to_trigger(driver)
    # OPEN LENGTH MENU
    clip_length_menu = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[1]/div[2]/button"))
    )
    clip_length_menu.click()
    time.sleep(10)
    # SELECT FIRST OPTION TO RESET SELECTION
    clip_length_menu_first_option = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[4]/div/div/div/div/div/div/div[1]"))
    )
    clip_length_menu_first_option.click()

    # SELECT LENGTH OPTIONS
    for i in short_length_selection:
        length_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 f"/html/body/div[4]/div/div/div/div/div/div/div[{i}]"))
        )
        length_option.click()

    # CLOSE MENU
    clip_length_menu.click()
    scroll_to_trigger(driver)
    scroll_to_trigger(driver)
    # my_templates_button CLICK
    my_templates_button = driver.find_element(By.XPATH,
                                              "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[2]/button")
    driver.execute_script("arguments[0].scrollIntoView();", my_templates_button)

    my_templates_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[2]/button"))
    )
    my_templates_button.click()

    return jsonify({
        "status": "done"
    }), 200


@selenium_bp.route('/opuspro/execute_submission/<instance_id>', methods=['POST'])
def execute_submission(instance_id):
    """Navigate the browser for a given Selenium instance."""
    data = request.json

    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        return jsonify({"error": "Invalid instance_id"}), 404

    initial_url = driver.current_url

    ## Input Video Link
    execute_submission_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/main/div/div[2]/div/div/div/div[1]/div[2]/div[2]/button"))
    )
    execute_submission_button.click()

    loading = True
    tries = 10
    start_point = 0
    while loading:
        current_url = driver.current_url
        if start_point >= tries:
            return jsonify({
                "error": "did not redirect to video processing page."
            }), 500
        elif current_url != initial_url:
            project_id = current_url.split("https://clip.opus.pro/dashboard?projectId=")[1]
            return jsonify({
                "opus_link": f"{initial_url}",
                "project_id": f"{project_id}"
            }), 200
        else:
            start_point += 1
        time.sleep(3)


# @selenium_bp.route('/opuspro/get_clips/<instance_id>', methods=['POST'])
# def get_opuspro_clips(instance_id):
#     """Navigate the browser for a given Selenium instance and process clips."""
#     data = request.json
#     clip_id = data.get('clip_id')
#     video_id = data.get('video_id')
#     category = data.get('category')
#     clip_section = "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div"
#     clips_tags = "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]"
#
#     if not clip_id:
#         return jsonify({"error": "Invalid instance_id"}), 404
#
#     driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
#     if not driver:
#         return jsonify({"error": "Invalid instance_id"}), 404
#
#     time.sleep(4)
#
#     # Scroll the page to load all clips
#     xpath = "//*[@id='dashboard-layout-container']"
#     try:
#         scrollable_element = driver.find_element(By.XPATH, xpath)
#         scroll_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_element)
#         client_height = driver.execute_script("return arguments[0].clientHeight;", scrollable_element)
#         if scroll_height > client_height:
#             for _ in range(20):  # Adjust scroll range as needed
#                 driver.execute_script("arguments[0].scrollTop += 50000;", scrollable_element)
#                 time.sleep(0.8)
#     except Exception as e:
#         print(f"Scrolling error: {e}")
#
#     try:
#         get_clips_section = driver.find_elements(By.XPATH, clip_section)
#         if len(get_clips_section) == 0:
#             get_clips_section = driver.find_elements(By.XPATH, "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]")
#             clipanything = True
#     except Exception as e:
#         print('failed')
#         return jsonify({"error": f"{e}"}), 500
#
#     output_counter = 0
#     for counter, get_clips_section in enumerate(get_clips_section, start=1):
#         clip_id = f"{clip_id}_{counter}"
#         try:
#             # Find the like button inside the clip
#             if not clipanything:
#                 like_button = get_clips_section.find_element(By.XPATH, f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[2]/div/div[1]/div[1]/span[1]/button")
#
#                 svg_element = like_button.find_element(By.TAG_NAME, "svg")
#
#                 # Get the class attribute of the SVG
#                 svg_class = svg_element.get_attribute("class")
#                 print(f"Clip {counter}: SVG class = {svg_class}")
#             else:
#                 like_button = get_clips_section.find_element(By.XPATH,
#                                                              f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]/section/div[2]/div[{counter}]/div/div[2]/div/div[1]/div[1]/span[1]/button")
#
#                 svg_element = like_button.find_element(By.TAG_NAME, "svg")
#
#                 # Get the class attribute of the SVG
#                 svg_class = svg_element.get_attribute("class")
#                 print(f"Clip {counter}: SVG class = {svg_class}")
#
#             if "text-red-400" in svg_class:
#                 if not clipanything:
#                     print(f"Clip {counter} is liked")
#
#                     # video_source = get_clips_section.find_element(By.XPATH, ".//video/source")
#                     download_button = driver.find_element(By.XPATH, f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[2]/div/div[3]/div[1]/span[2]/button")
#                     # ActionChains(driver).move_to_element(download_button).click().perform()
#                     # driver.execute_script("arguments[0].click();", download_button)
#                     download_button.send_keys(Keys.ENTER)
#                     print('test')
#                     time.sleep(10)
#                     file_name = os.listdir(TEMPORARY_DOWNLOAD_FOLDER)[0]
#                     try:
#                         move_file_to_target(video_id, clip_id, category)
#                     except Exception as e:
#                         time.sleep(10)
#                         move_file_to_target(video_id, clip_id, category)
#                     title = driver.find_element(By.XPATH,
#                                                 f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#                     captions = driver.find_element(By.XPATH, f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#                 else:
#                     print(f"Clip {counter} is liked")
#
#                     download_button = driver.find_element(By.XPATH, f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]/section/div[2]/div[{counter}]/div/div[2]/div/div[3]/div[1]/span[2]/button")
#                     # driver.execute_script("arguments[0].click();", download_button)
#                     download_button.send_keys(Keys.ENTER)
#                     # ActionChains(driver).move_to_element(download_button).click().perform()
#                     print('test')
#                     time.sleep(10)
#                     file_name = os.listdir(TEMPORARY_DOWNLOAD_FOLDER)[0]
#                     try:
#                         move_file_to_target(video_id, clip_id, category)
#                     except Exception as e:
#                         time.sleep(10)
#                         move_file_to_target(video_id, clip_id, category)
#
#                     title = driver.find_element(By.XPATH,
#                                                 f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#                     captions = driver.find_element(By.XPATH,
#                                                    f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#                     output_counter += 1
#
#                 # Process video (using process_video function)
#                 # video_process_data = process_video(video_id, title, captions, clip_id, counter, category)
#                 # video_filename = video_process_data["video_filename"]
#                 # clip_id = video_process_data["clip_id"]
#                 requests.post(
#                     url='http://localhost:5678/webhook/add_youtube_clip',
#                     json={
#                         "video_id": video_id,
#                         "title": title,
#                         "category": category,
#                         "video_name": file_name,
#                         "clip_id": clip_id,
#                         "captions": captions
#                     },
#                 )
#                 print(f'added a clip | main video_id {video_id} | category {category}')
#             else:
#                 print(f"Skipping unliked clip {counter}")
#                 continue
#         except Exception as e:
#             print(f"Error processing clip {counter}: {e}")
#
#     return jsonify({"status": "Completed processing clips", "total_clips": output_counter}), 200


@selenium_bp.route('/opuspro/get_clips/<instance_id>', methods=['POST'])
def get_opuspro_clips(instance_id):
    """
    Navigate the browser for a given Selenium instance and process clips.
    This version:
      - Avoids overshadowing variables
      - Uses relative XPaths inside the loop
      - Prints debug info so you can see each iteration
    """

    data = request.json
    base_clip_id = data.get('clip_id')
    video_id = data.get('video_id')
    category = data.get('category')

    print(f"DEBUG: Incoming request with instance_id={instance_id}, "
          f"clip_id={base_clip_id}, video_id={video_id}, category={category}")

    # Basic validation
    if not base_clip_id:
        print("DEBUG: Missing clip_id in request!")
        return jsonify({"error": "Invalid clip_id"}), 400

    driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
    if not driver:
        print("DEBUG: No Selenium driver found for instance_id!")
        return jsonify({"error": "Invalid instance_id"}), 404

    # Wait/scroll so all clips load
    time.sleep(4)

    # Example scrolling to reveal all clips
    # (If your page doesn't need scrolling, remove it.)
    xpath_scroll_container = "//*[@id='dashboard-layout-container']"
    try:
        scrollable_element = driver.find_element(By.XPATH, xpath_scroll_container)
        scroll_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_element)
        client_height = driver.execute_script("return arguments[0].clientHeight;", scrollable_element)

        # We do multiple scroll attempts if the content is bigger
        if scroll_height > client_height:
            print("DEBUG: Attempting to scroll to reveal more clips...")
            for i in range(20):  # Adjust the range as needed
                driver.execute_script("arguments[0].scrollTop += 999999;", scrollable_element)
                time.sleep(0.8)
    except Exception as e:
        print(f"DEBUG: Scrolling error: {e}")

    # Try locating the clip containers with your known XPaths
    # We'll first try one, if not found we try the fallback
    try:
        print("DEBUG: Trying to find main clip containers...")
        clips_list = driver.find_elements(By.XPATH, "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div")

        clipanything = False
        if len(clips_list) == 0:
            print("DEBUG: Found 0 in primary location, trying fallback location...")
            clips_list = driver.find_elements(By.XPATH, "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[3]/section/div[2]/div")
            clipanything = True

        print(f"DEBUG: Found {len(clips_list)} total clip elements.")
    except Exception as e:
        print(f"DEBUG: Exception while finding clip containers: {e}")
        return jsonify({"error": f"{e}"}), 500

    # If no clips are found at all, we can just return
    if len(clips_list) == 0:
        return jsonify({"status": "No clips found", "total_clips": 0}), 200

    output_counter = 0

    # Loop over the found elements
    for counter, clip_element in enumerate(clips_list, start=1):
        # Build a new clip_id for this iteration
        this_clip_id = f"{base_clip_id}_{counter}"
        print(f"\n=== DEBUG: Starting iteration {counter}/{len(clips_list)} for clip_id={this_clip_id} ===")

        try:
            # 1) Within this clip_element, find the like button with a RELATIVE XPATH.
            #    The dot at the start means "search inside clip_element"
            #    Adjust this to your actual structure as needed.
            #    If you absolutely must use an absolute path, that can cause issues on iteration 2, so be careful.
            if not clipanything:
                like_button = clip_element.find_element(By.XPATH, ".//div/div[2]/div/div[1]/div[1]/span[1]/button")
            else:
                like_button = clip_element.find_element(By.XPATH, ".//div/div[2]/div/div[1]/div[1]/span[1]/button")

            svg_element = like_button.find_element(By.TAG_NAME, "svg")
            svg_class = svg_element.get_attribute("class")
            print(f"DEBUG: Clip {counter}: SVG class = {svg_class}")

            # 2) Check if it's liked
            if "text-red-400" in svg_class:
                print(f"DEBUG: Clip {counter} is liked => we will attempt to download and move.")

                # 3) Also find the download button relative to the same clip_element
                try:
                    if not clipanything:
                        download_button = clip_element.find_element(By.XPATH, ".//div/div[2]/div/div[3]/div[1]/span[2]/button")
                    else:
                        download_button = clip_element.find_element(By.XPATH, ".//div/div[2]/div/div[3]/div[1]/span[2]/button")

                    # Perform the click
                    download_button.send_keys(Keys.ENTER)
                    print("DEBUG: Clicked on the download button, waiting for file to appear...")

                    # 4) Wait for the file to finish downloading
                    time.sleep(10)  # adjust if needed
                    all_files = os.listdir(TEMPORARY_DOWNLOAD_FOLDER)
                    if not all_files:
                        print("DEBUG: No files in TEMPORARY_DOWNLOAD_FOLDER after 10s??? Check if downloads are working.")
                        continue
                    file_name = all_files[0]
                    print(f"DEBUG: Found downloaded file: {file_name}")

                    # 5) Attempt to move the file
                    try:
                        move_file_to_target(video_id, this_clip_id, category)
                    except Exception as e:
                        print(f"DEBUG: Move file exception: {e}, retrying...")
                        time.sleep(10)
                        move_file_to_target(video_id, this_clip_id, category)

                    # 6) Grab the title/captions
                    #    Again, relative XPATH so we don't break on iteration 2
                    try:
                        title_element = clip_element.find_element(By.XPATH, ".//div/div[1]/div/div[1]/div/span")
                        title = title_element.text.strip()
                    except:
                        print("DEBUG: Could not find title element, setting to 'Untitled'")
                        title = "Untitled"

                    captions = title  # If they're the same?

                    # 7) Post data to your local webhook
                    requests.post(
                        url='http://localhost:5678/webhook/add_youtube_clip',
                        json={
                            "video_id": video_id,
                            "title": title,
                            "category": category,
                            "video_name": file_name,
                            "clip_id": this_clip_id,
                            "captions": captions
                        },
                    )
                    print(f"DEBUG: Sent POST to /webhook/add_youtube_clip for clip_id={this_clip_id}")

                    # 8) Increment the counter of processed clips
                    output_counter += 1

                except Exception as e:
                    print(f"DEBUG: Error clicking download or moving file for clip {counter}: {e}")
                    # Skip or continue
            else:
                print(f"DEBUG: Clip {counter} is NOT liked => skipping.")
                continue

        except Exception as e:
            print(f"DEBUG: Error processing clip {counter}: {e}")
            # You might want to continue here or break.
            # Usually you'd continue so you can try the next clip.
            continue

    # Done looping
    print(f"\nDEBUG: Loop finished. Processed {output_counter} liked clips out of {len(clips_list)} found.")
    return jsonify({"status": "Completed processing clips", "total_clips": output_counter}), 200