import ChatUI from "../../lib/components/ChatUI";
import DefaultShell from "../../lib/components/DefaultShell";

export default function Page() {
  return (
    <DefaultShell>
      <ChatUI
        chatUrl="/api/rag/basic_chat"
        modelOptions={["llama3-70b-8192", "gpt-4o"]}
      />
    </DefaultShell>
  );
}
