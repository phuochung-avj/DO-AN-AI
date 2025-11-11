"""
MODELS - Cấu trúc dữ liệu
==========================
Chứa các lớp dữ liệu cơ bản cho bài toán xếp lịch
"""


class Match:
    """
    Lớp đại diện cho một trận đấu
    
    Attributes:
        team1: Số thứ tự đội 1
        team2: Số thứ tự đội 2
        day: Ngày thi đấu (chưa xếp thì = -1)
        stadium: Sân vận động (chưa xếp thì = -1)
    """
    
    def __init__(self, team1: int, team2: int, day: int = -1, stadium: int = -1):
        self.team1 = team1  # Đội 1
        self.team2 = team2  # Đội 2
        self.day = day      # Ngày thi đấu (chưa xếp thì = -1)
        self.stadium = stadium  # Sân vận động (chưa xếp thì = -1)
    
    def __repr__(self):
        return f"Match(Đội {self.team1} vs Đội {self.team2}, Ngày {self.day}, Sân {self.stadium})"

