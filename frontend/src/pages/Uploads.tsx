import { useState } from "react"

export default function Uploads() {

    const [file, setFile] = useState<File | null>(null)
    const [url, setUrl] = useState<string | null>(null)
    const [uploading, setUploading] = useState(false)
    const [message, setMessage] = useState<string | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0] || null;

        setFile(selectedFile)
        setMessage("");
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if(!file) {
            setMessage("Please select a file to upload")
            return;
        }

        try {

            setUploading(true)
            setMessage("");

            const formData = new FormData();

            formData.append("file", file)

            const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Failed to upload file")
            }

            setUrl(data.url)

            setMessage("File uploaded successfully")

        } catch (error) {
            console.error("Error uploading file:", error)

            setMessage(error instanceof Error ? error.message : "An unknown error occurred")
        } finally {
            setUploading(false)
        }

    }

    return (
        <div>
            <h1>Uploads</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" name="file" onChange={handleFileChange} />
                
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