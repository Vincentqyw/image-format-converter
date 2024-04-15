import gradio as gr
from pathlib import Path
from PIL import Image

def get_supported_formats():
    """
    A function that retrieves the supported formats of images.
    Returns:
        The supported image formats as a list.
    """
    supported_formats = Image.registered_extensions()
    return supported_formats


SUPPORTED_FORMATS = get_supported_formats()


def convert_format(
    input_image: str = None, ext: str = ".webp", quality: int = 80
):
    """
    A function that converts an input image to a specified format with a given quality.

    Parameters:
        input_image (str): The path to the input image file.
        ext (str, optional): The extension for the output format. Defaults to ".webp".
        quality (int, optional): The quality of the output image. Defaults to 80.

    Returns:
        tuple: A tuple containing the reopened image in RGBA format and the path to the saved image file.
    """
    file_path = Path("caches") / "{}{}".format(Path(input_image).stem, ext)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_image)
    # img = img.convert("RGBA")
    format = None
    if ext in SUPPORTED_FORMATS:
        format = SUPPORTED_FORMATS[ext]
    if format is None:
        gr.Error(
            "Unsupported image format. Supported formats: {}".format(
                ", ".join(SUPPORTED_FORMATS)
            )
        )
    img.save(file_path, format, quality=quality)

    # reopen and check
    img_reopen = Image.open(file_path)
    img_reopen = img_reopen.convert("RGBA")
    return img_reopen, str(file_path)


def process(input_list: list[tuple], ext: str = ".webp", quality: int = 80):
    """
    A function that processes a list of images by converting them to a specified format with a given quality.

    Parameters:
        input_list (list[tuple]): A list of tuples containing the paths to the input image files.
        ext (str, optional): The extension for the output format. Defaults to ".webp".
        quality (int, optional): The quality of the output images. Defaults to 80.

    Returns:
        tuple: A tuple containing lists of file paths and reopened images in RGBA format.
    """
    out_files = []
    out_images = []
    for path in input_list:
        img_reopen, file_path = convert_format(path[0], ext, quality)
        out_files.append(file_path)
        out_images.append(img_reopen)
    return out_files, out_images


def swap_to_gallery(images: list):
    """
    A function that swaps to a gallery, taking a list of images as input.
    """
    return (
        gr.update(value=images, visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
    )


def run(server_name: str = "127.0.0.1", server_port: int = 7860):
    """
    A function that runs the WebP Converter app, allowing users to upload images, set quality, and convert them to WebP format.

    Parameters:
        server_name (str, optional): The server name where the app is hosted. Defaults to "127.0.0.1".
        server_port (int, optional): The port number for the server. Defaults to 7860.

    Returns:
        None
    """
    with gr.Blocks() as app:
        gr.Markdown(
            """
            # Image Format Converter
            Upload one or more image files and convert it to specified format with adjustable quality.
            ![]('F:/gradio-apps/image_to_webp/caches/1.webp')
            """
        )

        with gr.Row(equal_height=False):
            with gr.Column():
                files = gr.Files(
                    label="Drag 1 or more images",
                    file_types=["image"],
                )
                uploaded_files = gr.Gallery(
                    label="Your images", visible=False, columns=4, height="auto"
                )
                with gr.Row():
                    quality_slider = gr.Slider(
                        minimum=1,
                        maximum=100,
                        value=80,
                        step=1,
                        label="Image Quality",
                    )
                    extension_dropdown = gr.Dropdown(
                        label="Output Format",
                        choices=[
                            ".webp",
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".gif",
                            ".bmp",
                            ".tiff",
                            ".tif",
                        ],
                        value=".webp",
                    )
                with gr.Row():
                    reset_btn = gr.Button("Clear Images", variant="secondary")
                    proc_btn = gr.Button("Run Convert", variant="primary")

            with gr.Column():
                output_file = gr.File(label="Converted WebP")
                output_gallery = gr.Gallery(
                    label="Re-check converted images",
                    show_label=False,
                    elem_id="gallery",
                    object_fit="contain",
                    height="auto",
                    columns=4,
                )

        # collect inputs and outputs
        inputs = [
            uploaded_files,
            extension_dropdown,
            quality_slider,
        ]
        outputs = [
            output_file,
            output_gallery,
        ]

        # actions
        files.upload(
            fn=swap_to_gallery,
            inputs=files,
            outputs=[uploaded_files, proc_btn, files],
        )
        proc_btn.click(process, inputs=inputs, outputs=outputs)
        reset_btn.click(lambda: None, None, uploaded_files, queue=False)
    app.queue().launch(
        server_name=server_name, server_port=server_port, share=False
    )


if __name__ == "__main__":
    run(server_name="0.0.0.0", server_port=7860)
