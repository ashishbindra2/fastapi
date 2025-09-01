import io
import shutil
from os import path, makedirs
from pandas import read_csv, read_excel
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile):
    content_type = file.content_type
    file_name = file.filename
    
    # Define allowed file types
    allowed_types = [
        'image/jpeg', 'image/png', 'image/jpg', 'image/webp',
        'application/pdf', 'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    # Validate file type
    if content_type not in allowed_types:
        return JSONResponse(
            {"error": "Invalid file type. Allowed: jpeg, png, jpg, webp, pdf, csv, excel."},
            status_code=400
        )

    # Directory paths
    file_directories = {
        "application/pdf": "data/pdf_files/",
        "text/csv": "data/csv_files/",
        "application/vnd.ms-excel": "data/csv_files/",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "data/csv_files/",
        "image/jpeg": "data/image_files/",
        "image/png": "data/image_files/",
        "image/jpg": "data/image_files/",
        "image/webp": "data/image_files/"
    }

    directory = file_directories.get(content_type, "data/unknown_files/")
    makedirs(directory, exist_ok=True)
    file_path = path.join(directory, file_name)

    try:
        # Handle PDF
        if content_type == "application/pdf":
            with open(file_path, "wb") as f:
                f.write(await file.read())
            return {
                "file_name": file_name,
                "content_type": content_type,
                "file_path": file_path,
                "file_size_mb": f"{file.size / 1_048_576:.2f} MB",
            }

        # Handle CSV or Excel
        elif content_type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            # Read CSV file
            if content_type == "text/csv":
                df = read_csv(file_path)
            else:  # Read Excel file
                df = read_excel(file_path)
            
            return {
                "file_name": file_name,
                "columns": df.columns.tolist(),
                "sample_data": df.head(5).to_dict(orient="records")
            }

        # Handle Images
        else:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return {
                "file_name": file_name,
                "content_type": content_type,
                "file_path": file_path,
            }
    except Exception as e:
        return JSONResponse({"error": f"An error occurred: {str(e)}"}, status_code=500)
