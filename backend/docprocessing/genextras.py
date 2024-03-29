class GenerateExtras:
    def __init__(self) -> None:
        pass

    # Gets the links from the text of a document id:
    def extract_markdown_links(self, markdown_document_text: str) -> list[str]:
        # This regex pattern is designed to match typical markdown link structures
        markdown_url_pattern = r"!?\[.*?\]\((.*?)\)"
        # Find all non-overlapping matches in the markdown text
        urls = re.findall(markdown_url_pattern, markdown_document_text)
        return urls

    # Checks if the supplied DocumentID has a summary and if it doesnt it generates one and returns the docid.
    def generate_long_summary(
        self,
        document_text: str,
    ) -> DocumentID:
        # Check to see if a summary was already generated
        not_regen_summary = not regenerate_summary
        if (
            (docid.extras["summary"] == None)
            & (docid.extras["short_summary"])
            & not_regen_summary
        ):
            return docid
        processed_text = self.get_proc_doc(docid)
        summary_text = self.llm.summarize_document_text(processed_text)
        docid.extras["summary"] = summary_text
        short_summary_text = self.llm.gen_short_sum_from_long_sum(summary_text)
        docid.extras["short_summary"] = short_summary_text
        return docid

    def summarize_document_text(
        self, document_text: str, max_chunk_size: int = 5000
    ) -> str:
        chunked_document = token_split(document_text, max_chunk_size)

        # Function to summarize a single chunk of a document
        def summarize_chunk(document_chunk: str) -> str:
            prompt = f"Please summarize the following piece of text : \n\n {document_chunk} \n \n Please summarize the text above without saying anything else."
            summary = self.invoke([HumanMessage(content=prompt)])
            return summary.content

        # If the document can fit inside a single chunk just summarize the 1 chunk
        if len(chunked_document) == 1:
            return summarize_chunk(chunked_document[1])
        # Else break it up and summarize each chunk then recombine
        summarized_chunks = map(summarize_chunk, chunked_document)
        joined_summarized_chunks = "/n".join(summarized_chunks)
        condensed_summary = summarize_chunk(joined_summarized_chunks)
        return condensed_summary

    def llm_postprocess_audio(self, raw_text: str, chunk_size=1000) -> str:
        chunked_raw_text = token_split(raw_text, chunk_size)

        def process_chunk(transcript: str) -> str:
            prompt = f"""I want you to take the following transcript and trim out any filler words, sentence fragments, as well as any sentences that appear to be repeated or redundant. You should also use your rhetorical knowledge and experience about effective writing techniques in order to improve the grammar and flow of the transcript. Other then that I want you to change as little as possible and attempt to follow the transcript as closely and with as much detail as possible. Please do not skip over any paragraphs and make sure to transcribe everything.\n-BEGIN TRANSCRIPT-\n{transcript}\n-END TRANSCRIPT-\nNow write the accurate revised detailed transcript"""
            response = self.invoke([HumanMessage(content=prompt)])
            return response.content

        processed_chunks = map(process_chunk, chunked_raw_text)
        final_text = "\n".join(processed_chunks)
        return final_text

    def gen_short_sum_from_long_sum(self, long_sum_text: str) -> str:
        prompt = f"Please take the following summary of a document:\n{long_sum_text}\n And condense it into a 1-2 sentance summary. Return only the summary with no other instructions."
        short_summary = self.invoke([HumanMessage(content=prompt)])
        return short_summary.content
