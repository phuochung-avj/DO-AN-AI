import sys
from typing import List, Tuple, Set, Optional


def read_teams_from_input() -> List[str]:
	print("Nhập danh sách đội bóng, phân tách bằng dấu phẩy (ví dụ: A,B,C,D):", end=" ")
	line = sys.stdin.readline().strip()
	if not line:
		return ["A", "B", "C", "D"]
	teams = [name.strip() for name in line.split(",") if name.strip()]
	seen = set()
	unique_teams = []
	for t in teams:
		if t not in seen:
			seen.add(t)
			unique_teams.append(t)
	return unique_teams


def generate_round_robin_backtracking(teams: List[str]) -> List[List[Tuple[str, str]]]:
	bye_token: Optional[str] = None
	if len(teams) % 2 == 1:
		bye_token = "(BYE)"
		teams = teams + [bye_token]

	num_teams = len(teams)
	num_rounds = num_teams - 1
	teams_per_round = num_teams // 2

	all_pairs: Set[frozenset[str]] = set()
	for i in range(num_teams):
		for j in range(i + 1, num_teams):
			if bye_token is not None and (teams[i] == bye_token or teams[j] == bye_token):
				continue
			all_pairs.add(frozenset((teams[i], teams[j])))

	schedule: List[List[Tuple[str, str]]] = [[] for _ in range(num_rounds)]
	used_pairs: Set[frozenset[str]] = set()

	def build_round(round_index: int) -> bool:
		if round_index == num_rounds:
			return len(used_pairs) == len(all_pairs)

		used_in_round: Set[str] = set()
		pairs_this_round: List[Tuple[str, str]] = []

		def place_pair() -> bool:
			if len(pairs_this_round) == teams_per_round:
				schedule[round_index] = pairs_this_round.copy()
				return build_round(round_index + 1)

			first_team: Optional[str] = None
			for t in teams:
				if t not in used_in_round:
					first_team = t
					break
			if first_team is None:
				return False

			for other_team in teams:
				if other_team == first_team or other_team in used_in_round:
					continue

				pair_key = None if bye_token in (first_team, other_team) else frozenset((first_team, other_team))
				if pair_key is not None and pair_key in used_pairs:
					continue

				used_in_round.add(first_team)
				used_in_round.add(other_team)
				pairs_this_round.append((first_team, other_team))
				if pair_key is not None:
					used_pairs.add(pair_key)

				if place_pair():
					return True

				if pair_key is not None:
					used_pairs.remove(pair_key)
				pairs_this_round.pop()
				used_in_round.remove(first_team)
				used_in_round.remove(other_team)

			return False

		return place_pair()

	if build_round(0):
		for r in range(len(schedule)):
			schedule[r] = sorted(schedule[r], key=lambda ab: (ab[0], ab[1]))
		return schedule

	return []


def format_schedule_text(schedule: List[List[Tuple[str, str]]]) -> str:
	if not schedule:
		return "Không thể tạo lịch thi đấu hợp lệ."
	lines: List[str] = []
	for round_index, matches in enumerate(schedule, start=1):
		lines.append(f"Vòng {round_index}:")
		for home, away in matches:
			if "(BYE)" in (home, away):
				team = home if away == "(BYE)" else away
				lines.append(f"  {team} nghỉ")
			else:
				lines.append(f"  {home} vs {away}")
		lines.append("")
	return "\n".join(lines).strip()


def pretty_print_schedule(schedule: List[List[Tuple[str, str]]]) -> None:
	print(format_schedule_text(schedule))


def launch_gui() -> None:
	import tkinter as tk
	from tkinter import ttk

	root = tk.Tk()
	root.title("Xếp lịch thi đấu (Backtracking)")

	# Input frame
	frame_input = ttk.Frame(root, padding=10)
	frame_input.pack(fill="x")

	label = ttk.Label(frame_input, text="Nhập danh sách đội (phân tách dấu phẩy):")
	label.pack(anchor="w")

	teams_var = tk.StringVar(value="A,B,C,D")
	entry = ttk.Entry(frame_input, textvariable=teams_var)
	entry.pack(fill="x")

	# Buttons
	frame_btn = ttk.Frame(root, padding=(10, 0))
	frame_btn.pack(fill="x")

	def on_generate() -> None:
		text_output.configure(state="normal")
		text_output.delete("1.0", tk.END)
		teams_input = [name.strip() for name in teams_var.get().split(",") if name.strip()]
		if len(teams_input) < 2:
			text_output.insert(tk.END, "Cần ít nhất 2 đội để xếp lịch.")
			text_output.configure(state="disabled")
			return
		schedule = generate_round_robin_backtracking(teams_input)
		text_output.insert(tk.END, format_schedule_text(schedule))
		text_output.configure(state="disabled")

	btn = ttk.Button(frame_btn, text="Xếp lịch", command=on_generate)
	btn.pack(anchor="w")

	# Output
	frame_out = ttk.Frame(root, padding=10)
	frame_out.pack(fill="both", expand=True)

	text_output = tk.Text(frame_out, height=20, wrap="word")
	text_output.pack(side="left", fill="both", expand=True)

	scroll = ttk.Scrollbar(frame_out, orient="vertical", command=text_output.yview)
	scroll.pack(side="right", fill="y")
	text_output.configure(yscrollcommand=scroll.set)
	text_output.configure(state="disabled")

	root.mainloop()


def main() -> None:
	# Nếu chạy với --gui thì mở giao diện, ngược lại dùng CLI như cũ
	if any(arg.lower() == "--gui" for arg in sys.argv[1:]):
		launch_gui()
		return
	teams = read_teams_from_input()
	if len(teams) < 2:
		print("Cần ít nhất 2 đội để xếp lịch.")
		return
	schedule = generate_round_robin_backtracking(teams)
	pretty_print_schedule(schedule)


if __name__ == "__main__":
	main()
