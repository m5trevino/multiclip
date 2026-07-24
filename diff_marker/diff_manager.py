import difflib
from typing import List, Tuple
from .diff_types import DiffResult, DiffLine, DiffType

class DiffManager:
    def __init__(self):
        self.max_text_size = 1000000  # 1MB limit
        
    def calculate_diff(self, text1: str, text2: str, context_lines: int = 3) -> DiffResult:
        """Calculate differences between two texts"""
        
        # Validate input size
        if len(text1) > self.max_text_size or len(text2) > self.max_text_size:
            raise ValueError(f"Text size exceeds maximum limit of {self.max_text_size} characters")
        
        # Split into lines
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # Generate unified diff
        unified_diff = '\n'.join(difflib.unified_diff(
            lines1, lines2,
            fromfile='Text 1',
            tofile='Text 2',
            n=context_lines
        ))
        
        # Generate side-by-side diff data
        diff_lines = self._generate_side_by_side_diff(lines1, lines2)
        
        return DiffResult(
            lines=diff_lines,
            stats={},  # Will be calculated in __post_init__
            unified_diff=unified_diff
        )
    
    def _generate_side_by_side_diff(self, lines1: List[str], lines2: List[str]) -> List[DiffLine]:
        """Generate side-by-side diff representation"""
        diff_lines = []
        
        # Use SequenceMatcher for detailed comparison
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are identical
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        line_num_left=i + 1,
                        line_num_right=j1 + (i - i1) + 1,
                        content_left=lines1[i].rstrip('\n'),
                        content_right=lines2[j1 + (i - i1)].rstrip('\n'),
                        diff_type=DiffType.EQUAL
                    ))
            
            elif tag == 'delete':
                # Lines deleted from text1
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        line_num_left=i + 1,
                        line_num_right=None,
                        content_left=lines1[i].rstrip('\n'),
                        content_right="",
                        diff_type=DiffType.DELETE
                    ))
            
            elif tag == 'insert':
                # Lines inserted in text2
                for j in range(j1, j2):
                    diff_lines.append(DiffLine(
                        line_num_left=None,
                        line_num_right=j + 1,
                        content_left="",
                        content_right=lines2[j].rstrip('\n'),
                        diff_type=DiffType.INSERT
                    ))
            
            elif tag == 'replace':
                # Lines replaced
                max_lines = max(i2 - i1, j2 - j1)
                for k in range(max_lines):
                    left_idx = i1 + k if k < (i2 - i1) else None
                    right_idx = j1 + k if k < (j2 - j1) else None
                    
                    diff_lines.append(DiffLine(
                        line_num_left=left_idx + 1 if left_idx is not None else None,
                        line_num_right=right_idx + 1 if right_idx is not None else None,
                        content_left=lines1[left_idx].rstrip('\n') if left_idx is not None else "",
                        content_right=lines2[right_idx].rstrip('\n') if right_idx is not None else "",
                        diff_type=DiffType.REPLACE
                    ))
        
        return diff_lines
    
    def format_unified_diff(self, diff_result: DiffResult) -> str:
        """Return formatted unified diff"""
        return diff_result.unified_diff
    
    def get_diff_stats(self, diff_result: DiffResult) -> str:
        """Return formatted diff statistics"""
        stats = diff_result.stats
        return (f"Changes: +{stats['additions']} -{stats['deletions']} "
                f"~{stats['modifications']} (Total: {stats['total_lines']} lines)")