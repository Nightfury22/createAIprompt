import streamlit as st
import json
from datetime import datetime
from prompt_template import PROMPT_TEMPLATE
from gemini_service import generate_content_with_gemini
from parser import parse_gemini_response

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
                generated_content = parse_gemini_response(raw_gemini_response)

                st.success("Content generated successfully!")

                # Save to outputs directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"outputs/content_{timestamp}.json"
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(generated_content, f, indent=2, ensure_ascii=False)
                st.markdown(f"*Output saved to `{output_filename}`*", help="Check the `outputs` directory in your project.")

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
                        st.code(f"**Image Prompt:** {scene.get('image_prompt', 'N/A')}")
                        st.button("Copy Image Prompt", on_click=copy_to_clipboard, args=(scene.get("image_prompt", ""),), key=f"copy_image_prompt_{i}")
                        st.code(f"**Video Prompt:** {scene.get('video_prompt', 'N/A')}")
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