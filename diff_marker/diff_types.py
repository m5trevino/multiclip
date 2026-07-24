from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class DiffType(Enum):
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"

@dataclass
class DiffLine:
    line_num_left: Optional[int]
    line_num_right: Optional[int]
    content_left: str
    content_right: str
    diff_type: DiffType
    
@dataclass
class DiffResult:
    lines: List[DiffLine]
    stats: dict
    unified_diff: str
    
    def __post_init__(self):
        if not self.stats:
            self.stats = self._calculate_stats()
    
    def _calculate_stats(self) -> dict:
        stats = {
            'additions': 0,
            'deletions': 0,
            'modifications': 0,
            'total_lines': len(self.lines)
        }
        
        for line in self.lines:
            if line.diff_type == DiffType.INSERT:
                stats['additions'] += 1
            elif line.diff_type == DiffType.DELETE:
                stats['deletions'] += 1
            elif line.diff_type == DiffType.REPLACE:
                stats['modifications'] += 1
                
        return stats