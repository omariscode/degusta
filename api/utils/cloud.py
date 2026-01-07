import cloudinary
from dotenv import load_dotenv
from cloudinary import uploader


load_dotenv()

cloudinary.config(
    cloud_name="dsenmhltj",
    api_key="275671385831219",
    api_secret="dgcync47eYo7wIVO2CQli1zHSvM",
)

def upload_to_cloudinary_invoice(image_file):
    response = uploader.upload(image_file, folder="invoices")
    return response.get("secure_url")

def upload_to_cloudinary_marketing(image_file):
    response = uploader.upload(image_file, folder="marketing")
    return response.get("secure_url")

def upload_to_cloudinary_product(image_file):
    response = uploader.upload(image_file, folder="product")
    return response.get("secure_url")
