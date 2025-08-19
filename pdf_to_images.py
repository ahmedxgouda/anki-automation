from pdf2image import convert_from_path
import os

def main():
    # Get the path to the PDF file
    pdf_paths = get_pdf_paths()
    # Get the output folder
    for pdf_path in pdf_paths:
        output_folder = pdf_path.replace('.pdf', '')
        # Convert the PDF to images
        pdf_to_images(pdf_path, output_folder)

def get_pdf_paths():
    # Get the path to the PDF file
    pdf_path = input('Enter the path to the PDF file(s): ')
    pdf_paths = []
    for root, dirs, files in os.walk(pdf_path):
        if files:
            pdf_paths.extend([os.path.join(root, f) for f in files if f.endswith('.pdf')])
    return pdf_paths

def pdf_to_images(pdf_path, output_folder):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Save each image to the output folder
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i+1}.png')
        image.save(image_path, 'PNG')
        print(f'Saved: {image_path}')

if __name__ == '__main__':
    main()