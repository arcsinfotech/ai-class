import { useState } from "react";

interface Message {
    type: "human" | "assistant";
    content: string
}

export default function Sse() {

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>("");
    const [streaming, setStreaming] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => { 
        e?.preventDefault();

        const question = input.trim();

        if (!question || streaming) {
            return;
        }

        setMessages((prev) => [
            ...prev,
            {
                type: "human",
                content: question
            },
            {
                type: "assistant",
                content: ""
            }
        ])

        setInput("");
        setStreaming(true);

        try {

            const response = await fetch(`${import.meta.env.VITE_API_URL}/sse`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    question: question,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch");
            }

            if (!response.body) {
                throw new Error("No body");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let buffer = "";

            while(true) {
                const  { value, done } = await reader.read();

                if (done) {
                    break
                }

                buffer += decoder.decode(value, {
                    stream: true
                })

                
                buffer = buffer.replace(/\r\n/g, "\n")
                
                const events = buffer.split("\n\n");
                
                console.log(events);
                buffer = events.pop() || ""

                for  (const event of events) {
                    const dataline = event.split("\n").find((line) => line.startsWith("data:"));

                    if(!dataline) {
                        continue;
                    }

                    const data = dataline.replace(/^data:\s*/, "")

                    const payload = JSON.parse(data);

                    if (payload.data === "END") {
                        setStreaming(false);
                        return;
                    }

                    setMessages((prev) => {
                        const updated = [...prev];

                        const lastMessage = updated[updated.length -1];

                        if (lastMessage?.type === "assistant") {
                            updated[updated.length -1] = {
                                ...lastMessage,
                                content: lastMessage.content + payload.data
                            };
                        }

                        return updated;
                    })
                }
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setStreaming(false);
        }

    }


    return (
        <div>
            <h1>Server-Sent Events</h1>

            <div>
                {messages.map((message, index) => (
                    <div key={index}>
                        <p>
                            <strong>{message.type}: </strong>{message.content}
                        </p>
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit}>
                <input 
                    type="text"
                    value={input}
                    disabled={streaming}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask something..." 
                />

                <button
                    type="submit"
                    disabled={streaming || !input.trim()}
                >
                    {streaming ? "Generating..." : "Send"}
                </button>

            </form>

        </div>
    )
}