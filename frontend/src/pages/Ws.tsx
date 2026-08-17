import { useState } from "react"

interface Message {
    type: "human" | "assistant";
    content: string
}

export default function Ws() {

    const [messages, setMessage] = useState<Message[]>([]);
    const [input, setInput] = useState<string>('');
    const [streaming, setStreaming] = useState<boolean>(false);

    const handleSubmit = (e?: React.FormEvent<HTMLFormElement>) => {
        e?.preventDefault();

        const question = input.trim();

        if (!question || streaming) {
            return;
        }

        setMessage((prev) => [
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

        const ws = new WebSocket("ws://localhost:9000/ws")

        ws.onopen = () => {
            console.log("Websocket connected");

            ws.send(
                JSON.stringify({
                    question: question
                })
            );
        };

        ws.onmessage = (event) => {
            const payload = JSON.parse(event.data);

            if (payload.data === "END") {
                console.log("Streaming ended");
                setStreaming(false);
                ws.close();

                return;
            }

            setMessage((prev) => {
                const updated = [...prev]
                const lastMessage = updated[updated.length - 1];

                if (lastMessage?.type === "assistant") {
                    updated[updated.length -1] = {
                        ...lastMessage,
                        content: lastMessage.content + payload.data
                    };
                }
                return updated;
            })
        }

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            setStreaming(false);
            ws.close();
        }

        ws.onclose = () => {
            console.log("WebSocket closed");
            setStreaming(false);
        }

    }

    return (
        <div>
            <h1>WebSocket</h1>

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
                    placeholder="Ask Me Anything..."
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