import streamlit as st
import json
import traceback
from datetime import datetime
from prompt_template import PROMPT_TEMPLATE
from gemini_service import generate_content_with_gemini
from parser import parse_gemini_response
import os

print(f"DEBUG: app.py is importing generate_content_with_gemini from {generate_content_with_gemini.__module__}")
print(f"DEBUG: app.py is importing parse_gemini_response from {parse_gemini_response.__module__}")

# --- UI Configuration ---
st.set_page_config(layout="wide", page_title="AI Content Generator")
st.title("🎥 AI Story & Content Generator")

# --- Functions ---
def copy_to_clipboard(text):
    st.components.v1.html(f"<script>navigator.clipboard.writeText(`{text}`)</script>")

def download_json(data, filename="generated_content.json"):
    json_string = json.dumps(data, indent=2)
    st.download_button(
        label="Download JSON ⬇️",
        file_name=filename,
        mime="application/json",
        data=json_string,
    )

# --- Main Application Logic ---
user_prompt = st.text_area(
    "Enter your story concept:",
    "Pixar style short film about three Tamil boys drinking sugarcane juice during a hot summer.",
    height=150
)

if st.button("Generate Content 🚀", type="primary"):
    if not user_prompt:
        st.error("Please enter a prompt to generate content.")
    else:
        with st.spinner("Generating content with Gemini... This might take a moment."):
            try:
                full_prompt = PROMPT_TEMPLATE.format(user_prompt=user_prompt)
                raw_gemini_response = generate_content_with_gemini(full_prompt)
                print("RAW_GEMINI_RESPONSE:\n", repr(raw_gemini_response))
                try:
                    generated_content = parse_gemini_response(raw_gemini_response)
                except Exception as pe:
                    print("Parser error:\n", pe)
                    traceback.print_exc()
                    st.error(f"Parsing Error: {pe}. Check console for raw response.")
                    st.stop()

                st.success("Content generated successfully!")

                # Save to outputs directory

                # Create outputs directory
                os.makedirs("outputs", exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"outputs/content_{timestamp}"

                os.makedirs(output_dir, exist_ok=True)

                # -------------------------
                # Save full JSON
                # -------------------------
                json_file = os.path.join(output_dir, "content.json")

                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(generated_content, f, indent=2, ensure_ascii=False)

                # -------------------------
                # Save title
                # -------------------------
                with open(
                    os.path.join(output_dir, "title.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(generated_content.get("title", ""))

                # -------------------------
                # Save story
                # -------------------------
                with open(
                    os.path.join(output_dir, "story.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(generated_content.get("story", ""))

                # -------------------------
                # Save thumbnail prompt
                # -------------------------
                with open(
                    os.path.join(output_dir, "thumbnail_prompt.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(generated_content.get("thumbnail_prompt", ""))

                # -------------------------
                # Save YouTube description
                # -------------------------
                with open(
                    os.path.join(output_dir, "youtube_description.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(generated_content.get("youtube_description", ""))

                # -------------------------
                # Save hashtags
                # -------------------------
                hashtags = generated_content.get("hashtags", [])

                with open(
                    os.path.join(output_dir, "hashtags.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write("\n".join(hashtags))

                # -------------------------
                # Save image prompts
                # -------------------------
                with open(
                    os.path.join(output_dir, "image_prompts.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:

                    for scene in generated_content.get("scenes", []):
                        f.write(
                            f"Scene {scene.get('scene_number', '')}: "
                            f"{scene.get('scene_title', '')}\n"
                        )
                        f.write(scene.get("image_prompt", ""))
                        f.write("\n")
                        f.write("=" * 80)
                        f.write("\n\n")

                # -------------------------
                # Save video prompts
                # -------------------------
                with open(
                    os.path.join(output_dir, "video_prompts.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:

                    for scene in generated_content.get("scenes", []):
                        f.write(
                            f"Scene {scene.get('scene_number', '')}: "
                            f"{scene.get('scene_title', '')}\n"
                        )
                        f.write(scene.get("video_prompt", ""))
                        f.write("\n")
                        f.write("=" * 80)
                        f.write("\n\n")

                # -------------------------
                # Save scene details
                # -------------------------
                with open(
                    os.path.join(output_dir, "scenes.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:

                    for scene in generated_content.get("scenes", []):

                        f.write(
                            f"Scene {scene.get('scene_number', '')}\n"
                        )

                        f.write(
                            f"Title: {scene.get('scene_title', '')}\n\n"
                        )

                        f.write(
                            f"Description:\n{scene.get('description', '')}\n\n"
                        )

                        f.write("=" * 100)
                        f.write("\n\n")

                st.markdown(
                    f"✅ Output saved to `{output_dir}`"
                )
                # st.markdown(f"*Output saved to `{output_filename}`*", help="Check the `outputs` directory in your project.")

                # --- Display Results ---
                st.subheader("YouTube Video Title")
                st.code(generated_content.get("title", "N/A"))
                st.button("Copy Title", on_click=copy_to_clipboard, args=(generated_content.get("title", ""),), key="copy_title")

                st.subheader("Story")
                st.write(generated_content.get("story", "N/A"))
                st.button("Copy Story", on_click=copy_to_clipboard, args=(generated_content.get("story", ""),), key="copy_story")

                st.subheader("Scenes Breakdown")
                for i, scene in enumerate(generated_content.get("scenes", [])):
                    scene_number = scene.get("scene_number", i + 1)
                    scene_title = scene.get("scene_title", "")
                    with st.expander(f"Scene {scene_number}: {scene_title}"):
                        st.write(f"**Description:** {scene.get('description', 'N/A')}")
                        st.text_area(
                        "Image Prompt",
                        scene.get("image_prompt", ""),
                        height=150,
                        key=f"image_prompt_{i}",
                        )
                        st.button("Copy Image Prompt", on_click=copy_to_clipboard, args=(scene.get("image_prompt", ""),), key=f"copy_image_prompt_{i}")
                        st.text_area(
                            "Video Prompt",
                            scene.get("video_prompt", ""),
                            height=150,
                            key=f"video_prompt_{i}",
                        )
                        st.button("Copy Video Prompt", on_click=copy_to_clipboard, args=(scene.get("video_prompt", ""),), key=f"copy_video_prompt_{i}")

                st.subheader("Thumbnail Prompt")
                st.code(generated_content.get("thumbnail_prompt", "N/A"))
                st.button("Copy Thumbnail Prompt", on_click=copy_to_clipboard, args=(generated_content.get("thumbnail_prompt", ""),), key="copy_thumbnail_prompt")

                st.subheader("YouTube Description")
                st.write(generated_content.get("youtube_description", "N/A"))
                st.button("Copy YouTube Description", on_click=copy_to_clipboard, args=(generated_content.get("youtube_description", ""),), key="copy_yt_description")

                st.subheader("Hashtags")
                hashtags = " ".join(generated_content.get("hashtags", []))
                st.code(hashtags if hashtags else "N/A")
                st.button("Copy Hashtags", on_click=copy_to_clipboard, args=(hashtags,), key="copy_hashtags")

                st.markdown("--- توسعه --- ")
                download_json(generated_content, f"content_{timestamp}.json")

            except ValueError as ve:
                st.error(f"Input Error: {ve}")
            except RuntimeError as re:
                st.error(f"API Error: {re}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")