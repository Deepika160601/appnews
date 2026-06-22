
import uuid
import boto3

from fastapi import (
    HTTPException,
    UploadFile,
    status
)

from app.core.config import settings


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)


# =========================
# ALLOWED IMAGE TYPES
# =========================
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}


# =========================
# ALLOWED VIDEO TYPES
# =========================
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/mpeg",
    "video/quicktime",
    "video/x-msvideo"
}


# =========================
# ALLOWED DOCUMENT TYPES
# =========================
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png"
}


# =========================
# UPLOAD IMAGE
# =========================
async def upload_image_to_s3(
    file: UploadFile
):

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format"
        )

    extension = file.filename.split(".")[-1]

    file_name = (
        f"images/{uuid.uuid4()}.{extension}"
    )

    s3_client.upload_fileobj(
        file.file,
        settings.AWS_S3_BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return (
        f"https://{settings.AWS_S3_BUCKET_NAME}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{file_name}"
    )


# =========================
# UPLOAD VIDEO
# =========================
async def upload_video_to_s3(
    file: UploadFile
):

    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video format"
        )

    extension = file.filename.split(".")[-1]

    file_name = (
        f"videos/{uuid.uuid4()}.{extension}"
    )

    s3_client.upload_fileobj(
        file.file,
        settings.AWS_S3_BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return (
        f"https://{settings.AWS_S3_BUCKET_NAME}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{file_name}"
    )


# =========================
# UPLOAD DOCUMENT
# =========================
async def upload_document_to_s3(
    file: UploadFile
):

    if file.content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document format"
        )

    extension = file.filename.split(".")[-1]

    file_name = (
        f"documents/{uuid.uuid4()}.{extension}"
    )

    s3_client.upload_fileobj(
        file.file,
        settings.AWS_S3_BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return (
        f"https://{settings.AWS_S3_BUCKET_NAME}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{file_name}"
    )

