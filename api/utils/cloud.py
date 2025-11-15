import cloudinary
from dotenv import load_dotenv
from cloudinary import uploader


load_dotenv()

cloudinary.config(
    cloud_name="dbuox109b",
    api_key="847223172788564",
    api_secret="0Jh6eUB6YHS9qa_ZLS0jeBVx3H0",
)


def upload_to_cloudinary_invoice(image_file):
    response = uploader.upload(image_file, folder="invoices")
    return response.get("secure_url")


def upload_to_cloudinary_product(image_file):
    response = uploader.upload(image_file, folder="product")
    return response.get("secure_url")
