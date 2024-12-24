from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
import os, re
import json
import uuid
# from services.utils import hex_to_rgbcolor, clean_text
from configs.config import themes
import logging
from models.generative_model import get_model

model = get_model()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GENERATED_FILES_DIR = "data/generated"
os.makedirs(GENERATED_FILES_DIR, exist_ok=True)

def hex_to_rgbcolor(hex_color):
    """
    Converts a hex color string to a pptx RGBColor object.
    """
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return RGBColor(r, g, b)

def set_slide_background(slide, hex_color):
    """
    Sets the background color of a slide.
    """
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgbcolor(hex_color)

def add_text(slide, text, font_name, font_size, position, color="000000"):
    """
    Adds a textbox with the specified text to the slide.
    """
    textbox = slide.shapes.add_textbox(*position)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    p = text_frame.add_paragraph()
    p.text = text
    p.font.name = font_name
    p.font.size = Pt(font_size)
    p.font.color.rgb = hex_to_rgbcolor(color)

def add_bullet_points(slide, points, font_name, font_size, position, color="333333"):
    """
    Adds bullet points to a slide.
    """
    textbox = slide.shapes.add_textbox(*position)
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    for point in points:
        p = text_frame.add_paragraph()
        p.text = point
        p.font.name = font_name
        p.font.size = Pt(font_size)
        p.font.color.rgb = hex_to_rgbcolor(color)
        p.bullet = True
        p.level = 0  # Top-level bullet

def clean_text(text):
    """
    Removes markdown syntax like **, *, _, etc. from the text.
    """
    # Remove ** for bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove * for italic
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove __ for underline
    text = re.sub(r'__(.*?)__', r'\1', text)
    # Remove _ for underline
    text = re.sub(r'_(.*?)_', r'\1', text)
    return text


def create_presentation(content, theme_name="default"):
    """
    Creates a PowerPoint presentation based on the provided content and theme.
    """
    prs = Presentation()
    theme = themes.get(theme_name, themes["default"])

    for slide_content in content:
        layout = slide_content.get("layout", "bullet_points")

        if layout == "title":
            # Title slide layout (commonly index 0)
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            set_slide_background(slide, theme["background_color"])
            title_shape = slide.shapes.title
            title_shape.text = slide_content["title"]
            title_shape.text_frame.paragraphs[0].font.name = theme["font"]
            title_shape.text_frame.paragraphs[0].font.size = Pt(theme["font_size"] + 10)
            title_shape.text_frame.paragraphs[0].font.color.rgb = hex_to_rgbcolor(theme["title_color"])
            if "subtitle" in slide_content:
                add_text(
                    slide,
                    slide_content["subtitle"],
                    theme["font"],
                    theme["font_size"],
                    (Inches(1), Inches(3), Inches(8), Inches(1)),
                    theme["content_color"]
                )

        elif layout == "bullet_points":
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            set_slide_background(slide, theme["background_color"])
            title_shape = slide.shapes.title
            title_shape.text = slide_content["title"]
            title_shape.text_frame.paragraphs[0].font.name = theme["font"]
            title_shape.text_frame.paragraphs[0].font.size = Pt(theme["font_size"] + 5)
            title_shape.text_frame.paragraphs[0].font.color.rgb = hex_to_rgbcolor(theme["title_color"])
            body_shape = slide.shapes.placeholders[1]
            tf = body_shape.text_frame
            tf.clear()
            for point in slide_content["points"]:
                p = tf.add_paragraph()
                p.text = point
                p.bullet = True
                p.level = 0
                p.font.name = theme["font"]
                p.font.size = Pt(theme["font_size"])
                p.font.color.rgb = hex_to_rgbcolor(theme["content_color"])

        elif layout == "two_column":
            slide = prs.slides.add_slide(prs.slide_layouts[5])  # Use a blank layout
            set_slide_background(slide, theme["background_color"])
            # Add title
            add_text(
                slide,
                slide_content["title"],
                theme["font"],
                theme["font_size"] + 5,
                (Inches(1), Inches(0.5), Inches(8), Inches(1)),
                theme["title_color"]
            )
            # Add left column
            left_box = slide.shapes.add_textbox(Inches(1), Inches(1.7), Inches(4), Inches(4))
            left_tf = left_box.text_frame
            left_tf.word_wrap = True
            for point in slide_content.get("left_points", []):
                p = left_tf.add_paragraph()
                p.text = point
                p.bullet = True
                p.font.name = theme["font"]
                p.font.size = Pt(theme["font_size"])
                p.font.color.rgb = hex_to_rgbcolor(theme["content_color"])

            # Add right column
            right_box = slide.shapes.add_textbox(Inches(5.5), Inches(1.7), Inches(4), Inches(4))
            right_tf = right_box.text_frame
            right_tf.word_wrap = True
            for point in slide_content.get("right_points", []):
                p = right_tf.add_paragraph()
                p.text = point
                p.bullet = True
                p.font.name = theme["font"]
                p.font.size = Pt(theme["font_size"])
                p.font.color.rgb = hex_to_rgbcolor(theme["content_color"])

        elif layout == "content_with_image":
            slide = prs.slides.add_slide(prs.slide_layouts[5])  # Use a blank layout
            set_slide_background(slide, theme["background_color"])
            # Add title
            add_text(
                slide,
                slide_content["title"],
                theme["font"],
                theme["font_size"] + 5,
                (Inches(1), Inches(0.5), Inches(8), Inches(1)),
                theme["title_color"]
            )
            # Add content
            content_box = slide.shapes.add_textbox(Inches(1), Inches(1.7), Inches(5), Inches(4))
            content_tf = content_box.text_frame
            content_tf.word_wrap = True
            for line in slide_content.get("content", []):
                p = content_tf.add_paragraph()
                p.text = line
                p.bullet = True
                p.font.name = theme["font"]
                p.font.size = Pt(theme["font_size"])
                p.font.color.rgb = hex_to_rgbcolor(theme["content_color"])

            # Add image placeholder or actual image
            image_path = slide_content.get("image_path")
            if image_path and os.path.exists(image_path):
                slide.shapes.add_picture(image_path, Inches(7), Inches(1.7), width=Inches(2), height=Inches(2))
            else:
                placeholder = slide.shapes.add_textbox(Inches(7), Inches(1.7), Inches(2), Inches(2))
                placeholder.text = "Image Not Found"
                placeholder.text_frame.paragraphs[0].font.size = Pt(theme["font_size"])
                placeholder.text_frame.paragraphs[0].font.color.rgb = hex_to_rgbcolor(theme["content_color"])

        else:
            # Fallback to bullet_points layout if unrecognized layout
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            set_slide_background(slide, theme["background_color"])
            title_shape = slide.shapes.title
            title_shape.text = slide_content["title"]
            title_shape.text_frame.paragraphs[0].font.name = theme["font"]
            title_shape.text_frame.paragraphs[0].font.size = Pt(theme["font_size"] + 5)
            title_shape.text_frame.paragraphs[0].font.color.rgb = hex_to_rgbcolor(theme["title_color"])
            body_shape = slide.shapes.placeholders[1]
            tf = body_shape.text_frame
            tf.clear()
            for point in slide_content.get("points", []):
                p = tf.add_paragraph()
                p.text = point
                p.bullet = True
                p.level = 0
                p.font.name = theme["font"]
                p.font.size = Pt(theme["font_size"])
                p.font.color.rgb = hex_to_rgbcolor(theme["content_color"])

    return prs


def save_presentation(prs, topic, num_slides, theme, layouts):
    """
    Saves the presentation and its metadata.
    """
    presentation_id = str(uuid.uuid4())
    pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")
    prs.save(pptx_path)
    
    presentation_details = {
        "id": presentation_id,
        "topic": topic,
        "num_slides": num_slides,
        "theme": theme,
        "layouts": layouts,
        "download_url": f"/api/v1/presentations/{presentation_id}/download",
    }
    
    json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
    with open(json_path, 'w') as json_file:
        json.dump(presentation_details, json_file, indent=4)
    
    return presentation_details

def shorten_bullet_point(text, max_chars=120):
    """
    Shortens a bullet point to a maximum number of characters.
    """
    # Split by '.', keep the first sentence
    sentences = text.split('.')
    first_sentence = sentences[0].strip()
    # If it's too long, truncate
    if len(first_sentence) > max_chars:
        first_sentence = first_sentence[:max_chars].rstrip() + "..."
    return first_sentence

def fetch_content_from_gemini(topic, num_slides, layouts):
    """
    Fetches slide content from the Gemini LLM based on the topic, number of slides, and layouts.
    """
    prompt = f"Generate {num_slides} slides on the topic '{topic}'. Each slide should have a specific layout type. Provide titles and relevant content for each slide. Use the following format:\n\n"

    for i in range(num_slides):
        slide_num = i + 1
        layout = layouts[i]
        prompt += f"## Slide {slide_num}: Layout: {layout}\n"
        prompt += "Title: <Slide Title>\n"
        if layout == "title":
            prompt += "Subtitle: <Slide Subtitle>\n\n"
        elif layout == "bullet_points":
            prompt += "* Point 1\n* Point 2\n* Point 3\n\n"
        elif layout == "two_column":
            prompt += "Left:\n* Left Point 1\n* Left Point 2\n\n"
            prompt += "Right:\n* Right Point 1\n* Right Point 2\n\n"
        elif layout == "content_with_image":
            prompt += "Content:\n* Text line 1\n* Text line 2\n\n"
            prompt += "Image: <Image Placeholder>\n\n"

    prompt += "Ensure the layouts are clearly defined and content is concise."

    try:
        response = model.generate_content(prompt)
    except Exception as e:
        logger.error("Error generating content from Gemini: %s", e)
        raise

    candidates = response.candidates

    content = []
    for candidate in candidates:
        for part in candidate.content.parts:
            text = part.text
            slide_blocks = text.split("\n\n## Slide")
            slide_blocks = [block.strip() for block in slide_blocks if block.strip()]

            for block in slide_blocks:
                lines = block.split("\n")
                layout_line = next((line for line in lines if "Layout:" in line), None)
                if layout_line:
                    layout = layout_line.split("Layout:")[1].strip().lower()
                else:
                    layout = "bullet_points"  # Default layout

                title_line = next((line for line in lines if "Title:" in line), None)
                title = title_line.split("Title:")[1].strip() if title_line else "Untitled Slide"

                # Clean the title
                title = clean_text(title)

                slide_content = {"layout": layout, "title": title}

                if layout == "bullet_points":
                    bullet_points = [clean_text(line[2:].strip()) for line in lines if line.startswith("* ")]
                    slide_content["points"] = bullet_points

                elif layout == "two_column":
                    left_points = []
                    right_points = []
                    in_left = False
                    in_right = False
                    for line in lines:
                        if line.startswith("Left:"):
                            in_left = True
                            in_right = False
                        elif line.startswith("Right:"):
                            in_left = False
                            in_right = True
                        elif line.startswith("* ") and in_left:
                            left_points.append(clean_text(line[2:].strip()))
                        elif line.startswith("* ") and in_right:
                            right_points.append(clean_text(line[2:].strip()))
                    slide_content["left_points"] = left_points
                    slide_content["right_points"] = right_points

                elif layout == "content_with_image":
                    content_lines = [clean_text(line[2:].strip()) for line in lines if line.startswith("* ")]
                    slide_content["content"] = content_lines
                    image_line = next((line for line in lines if "Image:" in line), None)
                    slide_content["image_path"] = image_line.split("Image:")[1].strip() if image_line else None

                elif layout == "title":
                    subtitle_line = next((line for line in lines if "Subtitle:" in line), None)
                    subtitle = clean_text(subtitle_line.split("Subtitle:")[1].strip()) if subtitle_line else ""
                    slide_content["subtitle"] = subtitle

                # Default to bullet_points if layout is unrecognized
                else:
                    bullet_points = [clean_text(line[2:].strip()) for line in lines if line.startswith("* ")]
                    slide_content["points"] = bullet_points

                content.append(slide_content)
    return content
