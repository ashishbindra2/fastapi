from os import path
from os import walk
from os import makedirs

import multiprocessing

from pdf2image import convert_from_path

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

output_dir = "./static/output_images"

UPLOAD_DIRECTORY = './static/images'
POPPLER_PATH = r"C:\Users\Bindra\Downloads\Documents\Release-24.02.0-0\poppler-24.02.0\Library\bin"

NUM_CPUS = multiprocessing.cpu_count()

# Find all PDF files in the given directory
def find_pdfs(directory):
    pdf_files = []
    for root, _, files in walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(path.join(root, file))
    return pdf_files

# Save image with threading
def save_image(image, image_path, quality=95):
    image.save(image_path, 'PNG', quality=quality)
    print(f"Image saved: {image_path}")

# Convert a single PDF to images and save using threading
def process_pdf(pdf_path, start_count=0, dpi=300, quality=95, max_workers=4):
    try:
        print(f"Converting {pdf_path} to images...")

        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)
        image_paths = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, image in enumerate(images, start=start_count):  # Start counting from start_count
                image_path = path.join(UPLOAD_DIRECTORY, f"I{i + 1}.png")
                image_paths.append(image_path)
                futures.append(executor.submit(save_image, image, image_path, quality))
            
            for future in futures:
                future.result()  # Ensure all threads complete

        return len(images)  # Return the number of images processed for this PDF

    except Exception as e:
        print(f"Failed to convert pdf2img {pdf_path}: {e}")
        return 0

# Multiprocessing to handle multiple PDFs concurrently
def pdfs_to_images_multiprocessing(pdf_files, max_workers=None):
    image_counter = 0  # This will track the total number of images
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()  # Use all available CPUs
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = []
        for pdf in pdf_files:
            # Pass the current image counter as the starting point for numbering
            result = executor.submit(process_pdf, pdf, image_counter)
            num_images = result.result()  # Number of images processed by the current PDF
            image_counter += num_images  # Update the counter after each PDF

    return results
# def process_page(page_number, pdf_file, output_dir, start_count=0, dpi=300, quality=95, max_workers=4):
 

def pdf_to_images_multiprocessing(pdf_file, start_count = 1, dpi=300, quality=95, max_workers=None):
    """
    Convert a single page of a PDF to an image and save it.
    
    :param page_number: The page number to convert.
    :param pdf_file: The PDF file path.
    :param output_dir: The directory to save images.
    """
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()  # Use all available CPUs
    
    file_name = path.basename(pdf_file).replace('.pdf', '')
    file_path = path.join(output_dir, path.basename(file_name))
    # Create a directory to save the images
    makedirs(file_path, exist_ok=True)

   
    # Convert the specific page to an image
    images = convert_from_path(pdf_file,  dpi=dpi, poppler_path=POPPLER_PATH )
    
    try: 
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, image in enumerate(images, start=start_count):
                image_path = path.join(file_path, f"I{i}.png")

                futures.append(executor.submit(save_image, image, image_path, quality))

            for future in futures:
                future.result()  # Ensure all threads complete
    except Exception as e:
        print("Got error in Muti threading")
    return len(images) 

# import os
# from os import path, makedirs
# from pdf2image import convert_from_path
# from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
# import multiprocessing
# from functools import partial


# def save_image(image, image_path, quality):
#     """Save image to the file system."""
#     image.save(image_path, 'PNG', quality=quality)

# def convert_single_page(pdf_file, page_num, dpi):
#     """Convert a single page of the PDF to an image."""
#     images = convert_from_path(pdf_file, dpi=dpi, poppler_path=POPPLER_PATH, first_page=page_num, last_page=page_num)
#     return images[0]  # Return the single page image

# def pdf_to_images_mult(pdf_file, start_count=0, dpi=300, quality=95, max_workers=None):
#     """
#     Convert a PDF file to images using multiprocessing and save them with threading.
    
#     :param pdf_file: The PDF file path.
#     :param start_count: The starting index for naming images.
#     :param dpi: The DPI for image conversion.
#     :param quality: The quality of the saved images.
#     :param max_workers: Number of worker threads.
#     :return: Total number of images created.
#     """
#     if max_workers is None:
#         max_workers = multiprocessing.cpu_count()

#     # Prepare output directories
#     file_name = path.basename(pdf_file).replace('.pdf', '')
#     file_path = path.join(output_dir, file_name)
#     makedirs(file_path, exist_ok=True)

#     try:
#         # Get the total number of pages in the PDF by converting the first page
#         images = convert_from_path(pdf_file, dpi=dpi, poppler_path=POPPLER_PATH)
#         total_pages = len(images)

#         # Use multiprocessing to convert each page in parallel
#         with ProcessPoolExecutor(max_workers=max_workers) as process_executor:
#             convert_page_partial = partial(convert_single_page, pdf_file=pdf_file, dpi=dpi)
#             page_images = list(process_executor.map(convert_page_partial, range(1, total_pages + 1)))

#         # Save images using multithreading
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             futures = []
#             for i, image in enumerate(page_images, start=start_count):
#                 image_path = path.join(file_path, f"I_{i}.png")
#                 futures.append(executor.submit(save_image, image, image_path, quality))

#             for future in futures:
#                 future.result()  # Ensure all threads complete

#         return len(page_images)  # Return the number of images created
    
#     except Exception as e:
#         print(f"Error processing PDF: {e}")
#         return 0




if __name__ == '__main__':
    pdfs = find_pdfs('./data_pdf')

    if not path.exists(UPLOAD_DIRECTORY):
        makedirs(UPLOAD_DIRECTORY)

    num_cpus = multiprocessing.cpu_count()
    pdf_to_images_multiprocessing(pdfs, max_workers=num_cpus)
