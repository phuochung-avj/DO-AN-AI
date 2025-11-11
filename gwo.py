"""
GWO - Grey Wolf Optimizer
==========================
Giải bài toán xếp lịch bằng thuật toán GWO (Grey Wolf Optimizer)

Cách hoạt động:
1. Khởi tạo một đàn sói (các giải pháp ngẫu nhiên)
2. Mỗi sói đại diện cho một cách xếp lịch
3. Sắp xếp theo fitness: alpha (tốt nhất), beta, delta, omega (còn lại)
4. Các sói omega cập nhật vị trí dựa trên alpha, beta, delta
5. Lặp lại cho đến khi hội tụ hoặc đạt số lần lặp tối đa
"""

import random
import copy
from typing import List, Tuple, Dict
from models import Match
from evaluator import fitness_function


class GWOSolver:
    """
    Giải bài toán xếp lịch bằng thuật toán GWO (Grey Wolf Optimizer)
    """
    
    def __init__(self, data: Dict, num_wolves: int = 30, max_iterations: int = 100):
        self.data = data
        self.num_wolves = num_wolves  # Số lượng sói trong đàn
        self.max_iterations = max_iterations
        self.iterations = 0
    
    def initialize_wolf(self) -> List[Match]:
        """
        Khởi tạo một sói (một giải pháp ngẫu nhiên)
        Mỗi trận đấu được gán ngẫu nhiên một ngày và sân
        
        Returns:
            Một lịch thi đấu ngẫu nhiên
        """
        schedule = copy.deepcopy(self.data['matches'])
        num_matches = len(schedule)
        
        # Ước tính số ngày tối thiểu
        max_matches_per_day = self.data['max_matches_per_day']
        num_stadiums = self.data['num_stadiums']
        estimated_days = (num_matches + max_matches_per_day - 1) // max_matches_per_day
        
        for match in schedule:
            # Gán ngẫu nhiên ngày và sân
            day = random.randint(0, estimated_days * 2)  # Cho phép nhiều ngày hơn
            stadium = random.randint(0, self.data['num_stadiums'] - 1)
            match.day = day
            match.stadium = stadium
        
        return schedule
    
    def update_wolf_position(self, alpha: List[Match], beta: List[Match], 
                            delta: List[Match], omega: List[Match]) -> List[Match]:
        """
        Cập nhật vị trí của sói omega dựa trên alpha, beta, delta
        
        Trong GWO, omega cập nhật vị trí theo công thức:
        X_new = (X1 + X2 + X3) / 3
        Trong đó X1, X2, X3 là vị trí được tính từ alpha, beta, delta
        
        Args:
            alpha: Sói tốt nhất (alpha)
            beta: Sói tốt thứ 2 (beta)
            delta: Sói tốt thứ 3 (delta)
            omega: Sói cần cập nhật (omega)
        
        Returns:
            Sói omega mới sau khi cập nhật
        """
        new_schedule = copy.deepcopy(omega)
        a = 2.0 - (2.0 * self.iterations / self.max_iterations)  # Hệ số a giảm dần
        
        for i, match in enumerate(new_schedule):
            # Tính toán vị trí mới dựa trên alpha, beta, delta
            r1, r2 = random.random(), random.random()
            A = 2 * a * r1 - a
            C = 2 * r2
            
            # Vị trí từ alpha
            D_alpha = abs(C * alpha[i].day - omega[i].day)
            X1 = alpha[i].day - A * D_alpha
            
            # Vị trí từ beta
            r1, r2 = random.random(), random.random()
            A = 2 * a * r1 - a
            C = 2 * r2
            D_beta = abs(C * beta[i].day - omega[i].day)
            X2 = beta[i].day - A * D_beta
            
            # Vị trí từ delta
            r1, r2 = random.random(), random.random()
            A = 2 * a * r1 - a
            C = 2 * r2
            D_delta = abs(C * delta[i].day - omega[i].day)
            X3 = delta[i].day - A * D_delta
            
            # Vị trí mới (làm tròn và đảm bảo >= 0)
            new_day = int(round((X1 + X2 + X3) / 3))
            new_day = max(0, new_day)  # Đảm bảo ngày >= 0
            
            # Cập nhật sân: kết hợp thông tin từ alpha, beta, delta
            # Với xác suất dựa trên fitness, chọn sân từ các sói tốt
            rand_val = random.random()
            if rand_val < 0.4:  # 40% chọn từ alpha (tốt nhất)
                new_stadium = alpha[i].stadium
            elif rand_val < 0.7:  # 30% chọn từ beta
                new_stadium = beta[i].stadium
            elif rand_val < 0.9:  # 20% chọn từ delta
                new_stadium = delta[i].stadium
            else:  # 10% giữ nguyên hoặc ngẫu nhiên
                if random.random() < 0.5:
                    new_stadium = omega[i].stadium
                else:
                    new_stadium = random.randint(0, self.data['num_stadiums'] - 1)
            
            match.day = new_day
            match.stadium = new_stadium % self.data['num_stadiums']
        
        return new_schedule
    
    def repair_schedule(self, schedule: List[Match]) -> List[Match]:
        """
        Sửa chữa lịch để giảm vi phạm ràng buộc
        
        Args:
            schedule: Lịch cần sửa
        
        Returns:
            Lịch đã được sửa
        """
        repaired = copy.deepcopy(schedule)
        max_matches_per_day = self.data['max_matches_per_day']
        num_stadiums = self.data['num_stadiums']
        
        # Sắp xếp các trận đấu theo ngày
        repaired.sort(key=lambda x: x.day)
        
        # Đếm số trận mỗi ngày
        day_counts = {}
        for match in repaired:
            if match.day not in day_counts:
                day_counts[match.day] = []
            day_counts[match.day].append(match)
        
        # Sửa các ngày có quá nhiều trận
        current_day = 0
        for day, matches in sorted(day_counts.items()):
            if len(matches) > max_matches_per_day:
                # Di chuyển các trận thừa sang ngày khác
                for i in range(max_matches_per_day, len(matches)):
                    matches[i].day = current_day + 10 + i  # Đặt vào ngày xa hơn
                    matches[i].stadium = i % num_stadiums
        
        return repaired
    
    def solve(self) -> Tuple[List[Match], float, int]:
        """
        Giải bài toán bằng GWO
        
        Returns:
            Tuple (lịch tốt nhất, số ngày, số lần lặp)
        """
        # Khởi tạo đàn sói
        wolves = [self.initialize_wolf() for _ in range(self.num_wolves)]
        
        # Tính fitness cho mỗi sói
        fitness_scores = [fitness_function(self.data, wolf) for wolf in wolves]
        
        # Sắp xếp theo fitness
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
        
        best_schedule = None
        best_fitness = float('inf')
        
        for iteration in range(self.max_iterations):
            self.iterations = iteration + 1
            
            # Sắp xếp lại theo fitness
            sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
            
            # Alpha, beta, delta (3 sói tốt nhất)
            alpha_idx = sorted_indices[0]
            beta_idx = sorted_indices[1] if len(sorted_indices) > 1 else sorted_indices[0]
            delta_idx = sorted_indices[2] if len(sorted_indices) > 2 else sorted_indices[0]
            
            alpha = wolves[alpha_idx]
            beta = wolves[beta_idx]
            delta = wolves[delta_idx]
            
            # Cập nhật best
            if fitness_scores[alpha_idx] < best_fitness:
                best_fitness = fitness_scores[alpha_idx]
                best_schedule = copy.deepcopy(alpha)
            
            # Cập nhật các sói omega
            for i in range(self.num_wolves):
                if i not in [alpha_idx, beta_idx, delta_idx]:
                    # Cập nhật vị trí
                    new_wolf = self.update_wolf_position(alpha, beta, delta, wolves[i])
                    # Sửa chữa nếu cần
                    new_wolf = self.repair_schedule(new_wolf)
                    wolves[i] = new_wolf
                    fitness_scores[i] = fitness_function(self.data, new_wolf)
            
            # Đôi khi cập nhật cả alpha, beta, delta
            if iteration % 10 == 0:
                for idx in [alpha_idx, beta_idx, delta_idx]:
                    new_wolf = self.repair_schedule(wolves[idx])
                    wolves[idx] = new_wolf
                    fitness_scores[idx] = fitness_function(self.data, new_wolf)
        
        # Tính số ngày
        if best_schedule:
            days = max([m.day for m in best_schedule if m.day >= 0]) + 1
        else:
            days = float('inf')
        
        return best_schedule if best_schedule else wolves[0], days, self.iterations

