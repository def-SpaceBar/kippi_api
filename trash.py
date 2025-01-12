# def get_opuspro_clips(instance_id):
#     """Navigate the browser for a given Selenium instance."""
#     data = request.json
#     clip_id = data.get('clip_id')
#     video_id = data.get('video_id')
#     category = data.get('category')
#     clip_section = "/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]"
#     clips_tags = "//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]"
#
#     if not clip_id:
#         return jsonify({"error": "Invalid instance_id"}), 404
#
#     driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
#
#     if not driver:
#         return jsonify({"error": "Invalid instance_id"}), 404
#     time.sleep(5)
#
#     xpath = "//*[@id='dashboard-layout-container']"
#
#     try:
#         # Locate the scrollable element
#         scrollable_element = driver.find_element(By.XPATH, xpath)
#
#         # Check if the element is scrollable
#         scroll_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_element)
#         client_height = driver.execute_script("return arguments[0].clientHeight;", scrollable_element)
#
#         if scroll_height > client_height:
#             print(f"Element {xpath} is scrollable.")
#
#             # Attempt to scroll down
#             for _ in range(20):  # Adjust the range to scroll multiple times
#                 driver.execute_script("arguments[0].scrollTop += 5000;", scrollable_element)  # Scroll down by 50px
#                 time.sleep(0.5)  # Allow time for content to load
#
#                 # Get the new scroll position
#                 scroll_top = driver.execute_script("return arguments[0].scrollTop;", scrollable_element)
#                 print(f"Scrolled to: {scroll_top}")
#         else:
#             print(f"Element {xpath} is not scrollable.")
#     except Exception as e:
#         print(f"Error: {e}")
#
#     try:
#         # get_clips_section = WebDriverWait(driver, 5).until(
#         #     EC.visibility_of_element_located(
#         #         (By.XPATH, clip_section))
#         # )
#         parent_element = driver.find_element(By.XPATH, clips_tags)
#         get_clips_section = parent_element.find_elements(By.XPATH, ".//div")
#     except Exception as e:
#         print('failed')
#         return jsonify({"error": f"{e}"}), 500
#     time.sleep(4)
#     counter = 0
#     for i in get_clips_section:
#         print(i.get_attribute("outerHTML"))
#         counter += 1
#         container = i
#         like_button = container.find_element(By.XPATH, f".//div[{counter}]/div/div[2]/div/div[2]/span[1]/button")
#         like_svg = like_button.find_element(By.TAG_NAME, "svg")
#         # get_like_element = driver.find_element(By.XPATH, f"//html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[2]/div/div[2]/span[1]/button")
#         # svg_element = get_like_element.find_element(By.TAG_NAME, "svg")
#         print("SVG Class:", like_svg.get_attribute("class"))
#         print("SVG OuterHTML:", like_svg.get_attribute("outerHTML"))
#         # get_like_element = WebDriverWait(driver, 5).until(
#         #     EC.visibility_of_element_located(
#         #         (By.XPATH,
#         #          f"/div[{counter}]/div/div[2]/div/div[2]/span[1]/button/svg"))
#         # )
#         class_value = like_svg.get_attribute("class")
#         if class_value == "transition-all duration-600 text-red-400":
#             title = driver.find_element(By.XPATH,
#                                         f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#             captions = driver.find_element(By.XPATH,
#                                            f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#             # video_link = container.find_element(By.XPATH, f"//video")
#             video_link = container.find_element(By.TAG_NAME, "source").get_attribute('src')
#             print('video_id' + video_id)
#             print('title' + title)
#             print('captions' + captions)
#             print('clip_id' + clip_id)
#             print('video_link' + video_link)
#             print('counter' + str(counter))
#             print('category' + category)
#             video_process_data = process_video(video_id, title, captions, clip_id, video_link, counter, category)
#             video_path = video_process_data["video_path"]
#             captions_path = video_process_data["captions_path"]
#             title_path = video_process_data["title_path"]
#             requests.post(url='http://localhost:5678/webhook/add_youtube_clip', json={"video_id": video_id,
#                                                                                       "title": title,
#                                                                                       "captions": captions,
#                                                                                       "category": category,
#                                                                                       "video_path": video_path,
#                                                                                       "captions_path": captions_path,
#                                                                                       "title_path": title_path
#                                                                                       })
#         else:
#             print(f'skipped unliked video {counter}')
#             continue

#######################################################
#######################################################
#################### OPUS PRO #########################
#######################################################
#######################################################
# def get_opuspro_clips(instance_id):
#     """Navigate the browser for a given Selenium instance and process clips."""
#     data = request.json
#     clip_id = data.get('clip_id')
#     video_id = data.get('video_id')
#     category = data.get('category')
#
#     if not clip_id:
#         return jsonify({"error": "Invalid instance_id"}), 404
#
#     driver = ACTIVE_SELENIUM_INSTANCES.get(instance_id)
#     if not driver:
#         return jsonify({"error": "Invalid instance_id"}), 404
#     time.sleep(4)
#     # Scroll to ensure all content is loaded
#     xpath = "//*[@id='dashboard-layout-container']"
#     try:
#         scrollable_element = driver.find_element(By.XPATH, xpath)
#         scroll_height = driver.execute_script("return arguments[0].scrollHeight;", scrollable_element)
#         client_height = driver.execute_script("return arguments[0].clientHeight;", scrollable_element)
#         if scroll_height > client_height:
#             for _ in range(20):  # Adjust scroll range as needed
#                 driver.execute_script("arguments[0].scrollTop += 5000;", scrollable_element)
#                 time.sleep(0.5)
#     except Exception as e:
#         print(f"Scrolling error: {e}")
#
#     # Get fully rendered HTML content
#     html_content = driver.page_source
#     soup = BeautifulSoup(html_content, 'html.parser')
#
#     # Process clips using BeautifulSoup
#     clips = soup.select('#dashboard-layout-container div[data-state="open"]')  # Adjust selector as needed
#     results = []
#
#     for counter, clip in enumerate(clips, start=0):
#         like_button_svg = clip.select_one("button[aria-label='Like'] > svg")
#         like_button_svg_class = like_button_svg.get("class", "")
#         print(like_button_svg_class)
#         # Ensure the SVG element exists and check its class
#         if "text-red-400" in like_button_svg_class:
#             # title = clip.select_one("div.text-ellipsis span").get_text(strip=True)
#             # captions = clip.select_one("div.text-sm").get_text(strip=True)
#             title = driver.find_element(By.XPATH,
#                                         f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#             captions = driver.find_element(By.XPATH,
#                                            f"/html/body/div[1]/main/div/div[2]/div/div/div[2]/div[2]/section/div[2]/div[{counter}]/div/div[1]/div/div[1]/div/span").text
#             video_source = clip.select_one("video source")
#             video_link = video_source['src'] if video_source else None
#             # print('video_id' + video_id)
#             # print('title' + title)
#             # print('captions' + captions)
#             # print('clip_id' + clip_id)
#             # print('video_link' + video_link)
#             # print('counter' + str(counter))
#             # print('category' + category)
#             if not video_link:
#                 print(f"Skipping clip {counter}, no video source found.")
#                 continue
#
#             print(f"Processing liked clip {counter}: {title}")
#
#             # Process video data (existing process_video function)
#             video_process_data = process_video(video_id, title, captions, clip_id, video_link, counter, category)
#             video_path = video_process_data["video_path"]
#             captions_path = video_process_data["captions_path"]
#             title_path = video_process_data["title_path"]
#
#             # Post processed data to webhook
#             requests.post(
#                 url='http://localhost:5678/webhook/add_youtube_clip',
#                 json={
#                     "video_id": video_id,
#                     "title": title,
#                     "captions": captions,
#                     "category": category,
#                     "video_path": video_path,
#                     "captions_path": captions_path,
#                     "title_path": title_path,
#                 },
#             )
#         else:
#             print(f"Skipping unliked clip {counter}")
#
#
#     return jsonify({"status": "Completed processing clips", "total_clips": len(clips)}), 200