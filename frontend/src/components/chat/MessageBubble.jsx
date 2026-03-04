const REASON_TITLE = {
  NO_MATCH: "Tài liệu không đề cập",
  WEAK_EVIDENCE: "Không đủ chứng cứ",
  OUT_OF_SCOPE: "Ngoài phạm vi tài liệu",
};

const formatMaxScore = (value) => {
  if (typeof value !== "number" || Number.isNaN(value)) return "0.00";
  return value.toFixed(2);
};

const MessageBubble = ({ message }) => {
  if (message.type === "refusal") {
    const stats = message.retrievalStats || { nodes_found: 0, max_score: 0 };
    return (
      <div className={`bubble ${message.role}`}>
        <strong>{REASON_TITLE[message.reason] || "Từ chối trả lời"}</strong>
        <div>{message.content}</div>
        <div>
          nodes_found={stats.nodes_found}, max_score={formatMaxScore(stats.max_score)}
        </div>
      </div>
    );
  }

  return <div className={`bubble ${message.role}`}>{message.content}</div>;
};

export default MessageBubble;
