import tokenizers
import math


tokenizer = tokenizers.Tokenizer.from_pretrained("bert-base-uncased")


def token_split(string: str, max_length: int, overlap: int = 0) -> list:
    tokenlist = tokenizer.encode(string).ids
    num_chunks = math.ceil(len(tokenlist) / max_length)
    chunk_size = math.ceil(
        len(tokenlist) / num_chunks
    )  # Takes in an integer $n$ and then outputs the nth token for use in a map call.

    def make_index(token_id: int) -> str:
        begin_index, end_index = (
            chunk_size * token_id,
            chunk_size * (token_id + 1) + overlap,
        )
        tokens = tokenlist[begin_index:end_index]
        return_string = tokenizer.decode(tokens)
        return return_string

    chunk_ids = range(0, num_chunks - 1)
    return list(map(make_index, chunk_ids))


class LLM:
    def __init__(self, invoke_function):
        self.invoke_function = invoke_function

    def invoke(self, invokable):
        if isinstance(invokable, str):
            return self.invoke_function(
                [
                    SystemMessage(
                        "Please act as an assistant and answer the user's questions."
                    ),
                    HumanMessage(invokable),
                ]
            )
        return self.invoke_function(invokable)

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


# def test_token_split():
#     lorem = "On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue; and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided. But in certain circumstances and owing to the claims of duty or the obligations of business it will frequently occur that pleasures have to be repudiated and annoyances accepted. The wise man therefore always holds in these matters to this principle of selection: he rejects pleasures to secure other greater pleasures, or else he endures pains to avoid worse pains."
#     lorem_tokenized = [
#         "on the other hand, we denounce with righteous indignation",
#         "with righteous indignation and dislike men who are so beguiled and",
#         "so beguiled and demoralized by the charms of pleasure of the",
#         "charms of pleasure of the moment, so blinded by desire, that they cannot",
#         "desire, that they cannot foresee the pain and trouble that are bound to",
#         "trouble that are bound to ensue ; and equal blame belongs to those",
#         "equal blame belongs to those who fail in their duty through weakness of will,",
#         "through weakness of will, which is the same as saying through shrinking from to",
#         "saying through shrinking from toil and pain. these cases are perfectly simple and",
#         "cases are perfectly simple and easy to distinguish. in a free hour, when",
#         "a free hour, when our power of choice is untrammelled and",
#         "untrammelled and when nothing prevents our being able to do what we",
#         "able to do what we like best, every pleasure is to be welcomed and",
#         "is to be welcomed and every pain avoided. but in certain circumstances and owing",
#         "in certain circumstances and owing to the claims of duty or the obligations of business",
#         "or the obligations of business it will frequently occur that pleasures have to be rep",
#         "pleasures have to be repudiated and annoyances accepted. the wise man",
#         "accepted. the wise man therefore always holds in these matters to this principle of",
#         "matters to this principle of selection : he rejects pleasures to secure other greater pleasures",
#         "to secure other greater pleasures, or else he endures pains to avoid worse",
#     ]
#     result = token_split(lorem, 10, 5)
#     if result != lorem_tokenized:
#         return f"test failed tokenizer produced: {result} \n\n instead of: {lorem_tokenized}"
#     else:
#         return "test passed"
