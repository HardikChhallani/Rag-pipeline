from typing import List

class RecursiveTextChunker:
    """
    A custom chunker that attempts to split on logical boundaries (paragraphs, sentences)
    before falling back to character counts, ensuring we don't break in the middle of words.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text based on available separators."""
        final_chunks = []
        
        separator = separators[-1]
        for s in separators:
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                break
                
        # Split by the chosen separator
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
            
        good_splits = []
        for s in splits:
            if s:
                good_splits.append(s)
                
        # Merge splits up to chunk_size
        current_chunk = ""
        for s in good_splits:
            # Re-attach separator except for empty string
            s_with_sep = s + (separator if separator else "")
            
            if len(current_chunk) + len(s_with_sep) <= self.chunk_size:
                current_chunk += s_with_sep
            else:
                # If the single split is larger than chunk size, we need to split it further
                if len(s_with_sep) > self.chunk_size:
                    if len(separators) > 1:
                        # Recurse with finer separators
                        if current_chunk:
                            final_chunks.append(current_chunk.strip())
                            current_chunk = ""
                        sub_chunks = self._split_text(s, separators[1:])
                        final_chunks.extend(sub_chunks)
                    else:
                        # Fallback to hard character cut (should rarely happen)
                        if current_chunk:
                            final_chunks.append(current_chunk.strip())
                        current_chunk = s_with_sep[:self.chunk_size]
                else:
                    if current_chunk:
                        final_chunks.append(current_chunk.strip())
                    # Overlap handling: take the last `chunk_overlap` chars of the previous chunk
                    overlap = final_chunks[-1][-self.chunk_overlap:] if final_chunks and self.chunk_overlap > 0 else ""
                    current_chunk = overlap + " " + s_with_sep
                    
        if current_chunk:
            final_chunks.append(current_chunk.strip())
            
        # Clean up chunks
        return [c for c in final_chunks if len(c.strip()) > 0]
