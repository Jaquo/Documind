
from fastapi import FastAPI, File, UploadFile, HTTPException # this library allows us to create a web API and handle file uploads 
import pymupdf # this library allows us to read pdf files and extract text from them 
from chunking import chunk_document # this imports the chunk_document function from the chunking module



app = FastAPI(title="DocuMind API")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/") # @app.get("/") is a decorator that defines a GET endpoint for the root URL of the API. 
# When a GET request is made to the root URL, the home() function will be executed. 
def home(): # this function returns a simple JSON response indicating that the API is running. 
    return {
        "message": "Welcome to DocuMind",
        "status": "running"
    }


@app.post("/upload") # this decorator defines a POST endpoint for the URL "/upload". 
# When a POST request is made to this URL, the upload_pdf() function will be executed. 
async def upload_pdf(file: UploadFile = File(...)):

    # Check the filename
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # Read the uploaded file
    pdf_bytes = await file.read(MAX_FILE_SIZE + 1)
    await file.close()

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 10 MB or smaller."
        )

    # Check the file signature
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="This is not a valid PDF file."
        )

    # Open the PDF and extract its text
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:

            if document.needs_pass:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported yet."
                )

            page_count = document.page_count
            pages = []

            for page in document:
                pages.append(page.get_text())

    except (pymupdf.FileDataError, pymupdf.EmptyFileError):
        raise HTTPException(
            status_code=400,
            detail="The PDF could not be read."
        )

    # Combine the extracted text
    full_text = "\n".join(pages)
    # raises a full_text error if the PDF is empty or contains no readable text. 
    #The strip() method is used to remove any leading or trailing whitespace from the full_text string.

    if not full_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in this PDF."
        )


    # Split the document into chunks
    chunks = chunk_document(pages)

    # Return document information
    
    return {
        "filename": file.filename,
        "page_count": page_count,
        "characters_extracted": len(full_text),
        "total_chunks": len(chunks),

        "chunks_preview": [
            {
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "word_count": chunk["word_count"],
                "preview": chunk["text"][:150]
            }
            for chunk in chunks[:3]
        ]
    }


