// src/components/Linkified.jsx
import DOMPurify from "dompurify";
import linkifyHtml from "linkify-html";

export default function Linkified({ text }) {
  const html = DOMPurify.sanitize(
    linkifyHtml(text || "", { defaultProtocol: "https", target: "_blank", rel: "noopener noreferrer" })
  );
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
