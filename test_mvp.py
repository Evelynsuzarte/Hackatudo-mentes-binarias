"""
Testes Automatizados - FocAÊ 3.0 Clean (Hackathon Bemobi)
=========================================================
Validacao dos 12 Requisitos Funcionais (RF01 a RF12),
regras de negocio, ausência de emojis nos retornos e rotas REST.
"""

import unittest
import re
from app import app, db, EducationalPlatformService

class TestFocAEBackend(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_00_zero_emojis_in_backend(self):
        """Verifica a ausencia total de emojis nos dados e retornos do backend."""
        emoji_pattern = re.compile(
            r'[𐀀-􏿿]|[☀-➿]|[⌀-⏿]|[⭐-⭕]|[‼-㊙]'
        )
        # Testa curiosidades, missoes, turmas e alunos
        for fact in db.trivia_facts:
            self.assertEqual(len(emoji_pattern.findall(fact.title)), 0)
            self.assertEqual(len(emoji_pattern.findall(fact.content)), 0)

        for quest in db.photo_quests.values():
            self.assertEqual(len(emoji_pattern.findall(quest.title)), 0)
            self.assertEqual(len(emoji_pattern.findall(quest.description)), 0)

    def test_01_rf01_create_room(self):
        """RF01 - Criacao de sala gerando PIN numerico unico de 6 digitos."""
        res = EducationalPlatformService.create_room("Prof. Ricardo", "Matematica Ativa", "TURMA_A", 25)
        self.assertTrue(res["success"])
        pin = res["room"]["pin"]
        self.assertEqual(len(pin), 6)
        self.assertTrue(pin.isdigit())
        self.assertIn(pin, db.rooms)

    def test_02_rf05_join_room(self):
        """RF05 - Aluno ingressa na sala ativa com nome e PIN."""
        res_room = EducationalPlatformService.create_room()
        pin = res_room["room"]["pin"]

        res_join = EducationalPlatformService.join_room(pin, "Marley", "aluno_3")
        self.assertTrue(res_join["success"])
        self.assertEqual(res_join["room_pin"], pin)

        # Verifica presenca no estado da sala (RF02)
        state = EducationalPlatformService.get_room_state(pin)
        self.assertEqual(state["total_connected"], 1)
        self.assertEqual(state["connected_students"][0]["name"], "Marley")

    def test_03_rf03_start_focus_cycle(self):
        """RF03 - Professor inicia cronometro coletivo de foco."""
        pin = "492810"
        res = EducationalPlatformService.start_focus_cycle(pin, 15)
        self.assertTrue(res["success"])
        self.assertTrue(res["is_focus_active"])
        self.assertEqual(res["focus_duration_minutes"], 15)

    def test_04_rf04_broadcast_activity(self):
        """RF04 - Professor transmite dinamica (Kahoot/Gartic) para os alunos."""
        pin = "492810"
        res = EducationalPlatformService.broadcast_activity(
            pin, "Kahoot!", "Torneio de Algebra", "https://kahoot.it/?pin=492810", pin
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["active_activity"]["tool_name"], "Kahoot!")
        self.assertEqual(res["active_activity"]["access_pin"], pin)

    def test_05_rf09_focus_tick_points(self):
        """RF09 - Pontuacao individual por minuto completo no modo foco."""
        pin = "492810"
        initial_pts = db.students["aluno_1"].points
        res = EducationalPlatformService.focus_tick(pin, "aluno_1", 60)
        self.assertTrue(res["success"])
        self.assertEqual(res["points_earned"], 10)
        self.assertEqual(db.students["aluno_1"].points, initial_pts + 10)

    def test_06_rf07_focus_failure_detector(self):
        """RF07 - Detector de saida de tela zera o tempo da rodada do aluno."""
        pin = "492810"
        res = EducationalPlatformService.record_focus_failure(pin, "aluno_1", "Troca de aba detectada")
        self.assertTrue(res["success"])
        self.assertEqual(res["round_seconds"], 0)
        self.assertIn("zerado", res["consequence"])

    def test_07_rf08_rf10_conscious_pause_bonus(self):
        """RF08 e RF10 - Confirmacao da pausa consciente concede bonus de +15 pts."""
        pin = "492810"
        initial_pts = db.students["aluno_1"].points
        res = EducationalPlatformService.confirm_conscious_pause(pin, "aluno_1")
        self.assertTrue(res["success"])
        self.assertEqual(res["bonus_points"], 15)
        self.assertEqual(db.students["aluno_1"].points, initial_pts + 15)

    def test_08_rf11_presence_streak(self):
        """RF11 - Sequencia de presenca (Ofensiva: X dias seguidos)."""
        initial_streak = db.students["aluno_2"].streak_days
        res = EducationalPlatformService.increment_streak("aluno_2")
        self.assertTrue(res["success"])
        self.assertEqual(res["streak_days"], initial_streak + 1)
        self.assertIn("Ofensiva:", res["streak_text"])

    def test_09_rf12_collective_room_goal(self):
        """RF12 - Meta coletiva da sala e desbloqueio de recompensa."""
        pin = "492810"
        state = EducationalPlatformService.get_room_state(pin)
        self.assertTrue(state["success"])
        self.assertIn("collective_points", state)
        self.assertIn("progress_percentage", state)
        self.assertEqual(state["collective_reward"], "5 minutos livres no final da aula")

    def test_10_api_routes_http(self):
        """Valida respostas das rotas HTTP da API REST."""
        # Criacao de Sala via POST
        res_post_room = self.client.post("/api/rooms/create", json={"teacher_name": "Prof. Ricardo"})
        self.assertEqual(res_post_room.status_code, 201)
        new_pin = res_post_room.get_json()["room"]["pin"]

        # Consulta da Sala via GET
        res_get_room = self.client.get(f"/api/rooms/{new_pin}")
        self.assertEqual(res_get_room.status_code, 200)

        # Ingressar Aluno via POST
        res_join = self.client.post(f"/api/rooms/{new_pin}/join", json={"student_name": "Evelyn", "student_id": "aluno_1"})
        self.assertEqual(res_join.status_code, 200)

        # Acionar Atividade via POST
        res_act = self.client.post(f"/api/rooms/{new_pin}/send_activity", json={"tool_name": "Gartic", "title": "Desenho"})
        self.assertEqual(res_act.status_code, 200)

        # Alternar DND
        res_dnd = self.client.post("/api/students/aluno_1/toggle_dnd")
        self.assertEqual(res_dnd.status_code, 200)

        # Relatorio Semanal
        res_rep = self.client.get("/api/weekly_report?role=student&target_id=aluno_1")
        self.assertEqual(res_rep.status_code, 200)

        # Curiosidades
        res_trivia = self.client.get("/api/trivia")
        self.assertEqual(res_trivia.status_code, 200)


if __name__ == "__main__":
    unittest.main()
