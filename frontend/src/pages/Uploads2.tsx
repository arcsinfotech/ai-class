import { useState } from "react"

export default function Uploads() {

    const [file, setFile] = useState<File | null>(null)
    const [url, setUrl] = useState<string | null>(null)
    const [uploading, setUploading] = useState(false)
    const [message, setMessage] = useState<string | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0] || null;

        setFile(null);
        setUrl(null);
        setMessage("");

        if (!selectedFile) {
            return
        }

        if (selectedFile.type !== "application/pdf" ||
            !selectedFile.name.toLowerCase().endsWith(".pdf")
        ) {
            setMessage("Please select a PDF file")
            e.target.value = "";
            return;
        }

        setFile(selectedFile)
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!file) {
            setMessage("Please select a file to upload")
            return;
        }

        try {
            setUploading(true)
            setMessage("");
            setUrl(null);

            const response = await fetch(`${import.meta.env.VITE_API_URL}/upload2`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        filename: file.name,
                        content_type: file.type
                    }),
                }
            )

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Failed to upload file")
            }

            const uploadResponse = await fetch(
                data.signed_url,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/pdf"
                    },
                    body: file,
                }
            );

            if (!uploadResponse.ok) {
                throw new Error("Failed to upload file to storage")
            }

            setUrl(data.future_url);

            setMessage("File uploaded successfully");


        } catch (error) {
            console.error("Error uploading file:", error)
            setMessage(error instanceof Error ? error.message : "An unknown error occurred")

        } finally {
            setUploading(false)
        }

    }

    return (
        <div>
            <h1>Uploads File Client Side</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" name="file" onChange={handleFileChange} accept="application/pdf,.pdf" />
                
                {file && (
                    <p>
                        Selected file: {file.name}
                    </p>
                )}

                <button type="submit" disabled={!file || uploading}>
                    {uploading ? "Uploading..." : "Upload"}
                </button>

                {message && (
                    <p>{message}</p>
                )}

                {url && (
                    <p>
                        File URL: <a href={url} target="_blank">{url}</a>
                    </p>
                )}
            </form>
        </div>
    )
}