import sys
from typing import List, Tuple, Optional


def normalize_teams(raw_teams: List[str]) -> List[str]:
    cleaned = [t.strip() for t in raw_teams if t.strip()]
    if not cleaned:
        raise ValueError("Danh sách đội bóng trống.")
    # Loại bỏ trùng lặp nhưng vẫn giữ thứ tự
    seen = set()
    unique: List[str] = []
    for t in cleaned:
        if t.lower() not in seen:
            unique.append(t)
            seen.add(t.lower())
    return unique


def build_pairs(num_teams: int) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    for i in range(num_teams):
        for j in range(i + 1, num_teams):
            pairs.append((i, j))
    return pairs


def order_pairs_heuristic(pairs: List[Tuple[int, int]], num_teams: int) -> List[Tuple[int, int]]:
    # Heuristic: ưu tiên cặp có đội xuất hiện nhiều (theo bậc) để ràng buộc sớm
    degree = [0] * num_teams
    for a, b in pairs:
        degree[a] += 1
        degree[b] += 1
    return sorted(pairs, key=lambda ab: -(degree[ab[0]] + degree[ab[1]]))


def backtrack_schedule(num_teams: int) -> List[List[Tuple[int, int]]]:
    # Nếu số đội lẻ, thêm BYE (nghỉ)
    has_bye = (num_teams % 2 == 1)
    teams_with_bye = num_teams + 1 if has_bye else num_teams

    rounds_count = teams_with_bye - 1
    matches_per_round = teams_with_bye // 2

    all_pairs = build_pairs(teams_with_bye)
    all_pairs = order_pairs_heuristic(all_pairs, teams_with_bye)

    rounds: List[List[Tuple[int, int]]] = [[] for _ in range(rounds_count)]
    used_in_round: List[set] = [set() for _ in range(rounds_count)]

    def can_place(pair: Tuple[int, int], r: int) -> bool:
        a, b = pair
        if len(rounds[r]) >= matches_per_round:
            return False
        if a in used_in_round[r] or b in used_in_round[r]:
            return False
        return True

    def dfs(idx: int) -> bool:
        if idx == len(all_pairs):
            return True
        a, b = all_pairs[idx]
        # Tối ưu nhỏ: thử các vòng có khoảng trống trước
        candidate_rounds = sorted(range(rounds_count), key=lambda r: len(rounds[r]))
        for r in candidate_rounds:
            if can_place((a, b), r):
                rounds[r].append((a, b))
                used_in_round[r].add(a)
                used_in_round[r].add(b)
                if dfs(idx + 1):
                    return True
                rounds[r].pop()
                used_in_round[r].remove(a)
                used_in_round[r].remove(b)
        return False

    ok = dfs(0)
    if not ok:
        raise RuntimeError("Không thể sắp xếp lịch thi đấu với backtracking.")

    # Nếu có BYE, giữ nguyên chỉ số, người gọi sẽ lọc khi hiển thị
    return rounds


def mirror_double_round_robin(rounds: List[List[Tuple[int, int]]]) -> List[List[Tuple[int, int]]]:
    second_half: List[List[Tuple[int, int]]] = []
    for r in rounds:
        mirrored = [(b, a) for (a, b) in r]
        second_half.append(mirrored)
    return rounds + second_half


def format_schedule(rounds: List[List[Tuple[int, int]]], team_names: List[str]) -> str:
    has_bye = (len(team_names) % 2 == 1)
    bye_index: Optional[int] = None
    names = team_names
    if has_bye:
        bye_index = len(team_names)
        names = team_names + ["BYE"]

    lines: List[str] = []
    for i, r in enumerate(rounds, start=1):
        lines.append(f"Vòng {i}:")
        for a, b in r:
            # Ẩn trận có BYE khỏi danh sách
            if (bye_index is not None) and (a == bye_index or b == bye_index):
                continue
            home = names[a]
            away = names[b]
            lines.append(f"  - {home} vs {away}")
        lines.append("")
    return "\n".join(lines).rstrip()


def parse_input() -> Tuple[List[str], bool]:
    print("Nhập tên các đội, ngăn cách bởi dấu phẩy (ví dụ: A,B,C,D):")
    raw = sys.stdin.readline().strip()
    if not raw:
        print("Không nhập tên đội. Sẽ dùng tên mặc định: Team 1..n")
        print("Nhập số lượng đội (>=2):")
        n_str = sys.stdin.readline().strip()
        try:
            n = int(n_str)
        except Exception:
            raise ValueError("Số lượng đội không hợp lệ.")
        if n < 2:
            raise ValueError("Cần ít nhất 2 đội.")
        teams = [f"Team {i+1}" for i in range(n)]
    else:
        teams = normalize_teams(raw.split(","))
        if len(teams) < 2:
            raise ValueError("Cần ít nhất 2 đội.")

    print("Chế độ lượt đi-lượt về? (y/n, mặc định: n):")
    mode = sys.stdin.readline().strip().lower()
    double_rr = (mode == "y" or mode == "yes")
    return teams, double_rr


def main() -> None:
    try:
        teams, double_rr = parse_input()
        n = len(teams)

        # Xây lịch (thêm BYE nội bộ nếu lẻ)
        base_rounds = backtrack_schedule(n)
        rounds = mirror_double_round_robin(base_rounds) if double_rr else base_rounds

        output = format_schedule(rounds, teams)
        print("\nLịch thi đấu:")
        print(output)
    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()


