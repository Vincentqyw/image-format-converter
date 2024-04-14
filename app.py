import gradio as gr
from pathlib import Path
from PIL import Image


def convert_to_webp(input_image: str = None, quality=80):
    file_path = Path("caches") / "{}.{}".format(Path(input_image).stem, "webp")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_image)
    img = img.convert("RGBA")
    img.save(file_path, "WEBP", quality=quality)

    # reopen and check
    img_reopen = Image.open(file_path)
    img_reopen = img_reopen.convert("RGBA")
    return img_reopen, str(file_path)


def process(input_list, quality=80):
    out_files = []
    out_images = []
    for path in input_list:
        img_reopen, file_path = convert_to_webp(path[0], quality)
        out_files.append(file_path)
        out_images.append(img_reopen)
    return out_files, out_images


def swap_to_gallery(images):
    return (
        gr.update(value=images, visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
    )


def run(server_name="127.0.0.1", server_port=7860):
    with gr.Blocks() as app:
        gr.Markdown(
            """
            # WebP Converter
            Upload one or more image files and convert it to WebP format with adjustable quality.
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
                    label="Your images", visible=False, columns=4, height=250
                )
                inputs = [
                    uploaded_files,
                    gr.Slider(
                        minimum=1,
                        maximum=100,
                        value=80,
                        step=1,
                        label="Image Quality",
                    ),
                ]
                btn = gr.Button("Run Convert", variant="primary")

            with gr.Column():
                outputs = [
                    gr.File(label="Converted WebP"),
                    gr.Gallery(
                        label="Re-check converted images",
                        show_label=False,
                        elem_id="gallery",
                        object_fit="contain",
                        height="auto",
                        columns=4,
                        # height=125,
                    ),
                ]
        files.upload(
            fn=swap_to_gallery,
            inputs=files,
            outputs=[uploaded_files, btn, files],
        )
        btn.click(process, inputs=inputs, outputs=outputs)
    #
    app.queue().launch(
        server_name=server_name, server_port=server_port, share=False
    )


if __name__ == "__main__":
    run(server_name="0.0.0.0", server_port=7860)
