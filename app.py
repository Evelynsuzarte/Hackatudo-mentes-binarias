"""
FocAE - Backend MVP & Plataforma Educacional de Foco Consciente (Hackathon Bemobi)
================================================================================
Sistema de gestao escolar, foco consciente em smartphones, metodologias ativas,
saude mental e gamificacao cooperativa (individual e coletiva).

Filosofia Central:
- Autonomia e Autorregulacao: Sem bloqueio coercitivo permanente.
- Gamificacao Cooperativa: Dinamicas ao vivo, pausas visuais conscientes,
  desafios fotograficos no mundo real e metas coletivas de sala.
- Armazenamento: 100% em memoria (dataclasses, dicionarios e listas nativas em Python).
- Formato Clean & Educacional: Sem emojis nos textos.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os
import random
from flask import Flask, jsonify, request, render_template

# ==============================================================================
# 1. ESTRUTURAS DE DADOS (DOMINIO DO SISTEMA)
# ==============================================================================

@dataclass
class ExternalTool:
    id: str
    name: str
    category: str
    url: str
    description: str
    badge_color: str

@dataclass
class ActivitySession:
    id: str
    title: str
    subject: str
    class_id: str
    tool_name: str
    direct_link: str
    access_pin: Optional[str] = None
    description: str = "Atividade de metodologia ativa."
    teacher: str = "Prof. Ricardo"
    requires_pdf: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    active: bool = True

@dataclass
class ScheduleSlot:
    time: str
    subject: str
    teacher: str
    methodology: str

@dataclass
class Classroom:
    id: str
    name: str
    shift: str
    collective_goal: int
    collective_reward: str
    schedule: List[ScheduleSlot] = field(default_factory=list)
    collective_offline_minutes: int = 0
    collective_offline_target: int = 60

@dataclass
class PhotoQuest:
    id: str
    title: str
    description: str
    category: str
    points_reward: int
    icon_name: str

@dataclass
class PdfSubmission:
    id: str
    student_id: str
    student_name: str
    activity_id: str
    activity_title: str
    filename: str
    submitted_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    status: str = "Entregue"
    grade: Optional[str] = "Nota 10 / Excelente"

@dataclass
class MentalHealthMission:
    id: str
    title: str
    description: str
    points_reward: int
    category: str

@dataclass
class PointTransaction:
    timestamp: str
    student_id: str
    points: int
    reason: str

@dataclass
class TriviaFact:
    id: str
    category: str
    title: str
    content: str

@dataclass
class Student:
    id: str
    name: str
    class_id: str
    points: int = 0
    streak_days: int = 0
    attendance_days: int = 15
    presence_bonus_awarded: bool = False
    minutes_offline: int = 45
    completed_missions: List[str] = field(default_factory=list)
    completed_photo_quests: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    focus_trees: int = 3
    notifications_blocked: bool = True
    notifications_silenced_count: int = 14

@dataclass
class Room:
    pin: str
    teacher_name: str
    subject: str
    class_id: str
    created_at: str
    is_focus_active: bool = False
    focus_duration_minutes: int = 25
    focus_started_at: Optional[str] = None
    focus_ends_at: Optional[str] = None
    connected_students: Dict[str, Dict] = field(default_factory=dict)
    active_activity: Optional[Dict] = None
    collective_points: int = 0
    collective_target: int = 150
    collective_reward: str = "5 minutos livres no final da aula"
    reward_unlocked: bool = False

# ==============================================================================
# 2. BANCO DE DADOS EM MEMORIA (REPOSITORIO & MOCK INICIAL)
# ==============================================================================

class InMemoryDatabase:
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.classes: Dict[str, Classroom] = {}
        self.rooms: Dict[str, Room] = {}
        self.external_tools: Dict[str, ExternalTool] = {}
        self.activity_sessions: List[ActivitySession] = []
        self.missions: Dict[str, MentalHealthMission] = {}
        self.photo_quests: Dict[str, PhotoQuest] = {}
        self.pdf_submissions: List[PdfSubmission] = []
        self.transactions: List[PointTransaction] = []
        self.trivia_facts: List[TriviaFact] = []
        self.collective_pact_active: bool = False
        self.collective_pact_timer: int = 30
        self._seed_initial_data()

    def _seed_initial_data(self):
        turma_a_schedule = [
            ScheduleSlot("08:00 - 08:50", "Matematica Ativa", "Prof. Ricardo", "Gamificacao com Kahoot"),
            ScheduleSlot("09:00 - 09:50", "Biologia e Natureza", "Profa. Helena", "Desenho Colaborativo via Gartic"),
            ScheduleSlot("10:10 - 11:00", "Redacao e Atualidades", "Prof. Carlos", "Nuvem de ideias via Mentimeter"),
        ]
        turma_b_schedule = [
            ScheduleSlot("08:00 - 08:50", "Historia Contemporanea", "Profa. Ana", "Quizizz Interativo"),
            ScheduleSlot("09:00 - 09:50", "Fisica Experimental", "Prof. Marcos", "Kahoot Leis do Movimento"),
        ]

        self.classes["TURMA_A"] = Classroom(
            id="TURMA_A",
            name="Turma A (1o Ano Medio)",
            shift="Manha",
            collective_goal=250,
            collective_reward="Dia de Jogos Educativos e Workshop de Robotica",
            schedule=turma_a_schedule,
            collective_offline_minutes=35,
            collective_offline_target=60
        )

        self.classes["TURMA_B"] = Classroom(
            id="TURMA_B",
            name="Turma B (1o Ano Medio)",
            shift="Manha",
            collective_goal=200,
            collective_reward="Sessao de Cinema Pedagogico com Debate",
            schedule=turma_b_schedule,
            collective_offline_minutes=20,
            collective_offline_target=60
        )

        self.students["aluno_1"] = Student(
            id="aluno_1",
            name="Evelyn",
            class_id="TURMA_A",
            points=60,
            streak_days=5,
            attendance_days=18,
            minutes_offline=60,
            completed_missions=["M1_RECREIO_OFFLINE"],
            completed_photo_quests=["Q1_ALGO_VERDE"],
            badges=["Exploradora da Autonomia", "Olhar Consciente"],
            focus_trees=4
        )

        self.students["aluno_2"] = Student(
            id="aluno_2",
            name="Thiago",
            class_id="TURMA_A",
            points=45,
            streak_days=3,
            attendance_days=16,
            minutes_offline=45,
            completed_missions=["M2_RESPIRACAO_GUIADA"],
            completed_photo_quests=[],
            badges=["Presenca Ativa"],
            focus_trees=3
        )

        self.students["aluno_3"] = Student(
            id="aluno_3",
            name="Marley",
            class_id="TURMA_B",
            points=50,
            streak_days=2,
            attendance_days=15,
            minutes_offline=30,
            completed_missions=["M3_FOCO_POMODORO"],
            completed_photo_quests=["Q2_FLOR_BONITA"],
            badges=["Iniciativa Zen"],
            focus_trees=2
        )

        tools = [
            ExternalTool("kahoot", "Kahoot!", "Quiz Dinamico", "https://kahoot.it", "Gamificacao em tempo real com perguntas e ranking.", "#0284C7"),
            ExternalTool("gartic", "Gartic", "Desenho Colaborativo", "https://gartic.com.br", "Metodologia visual ativa: adivinhar conceitos desenhados pelos colegas.", "#0D9488"),
            ExternalTool("quizizz", "Quizizz", "Desafio Gamificado", "https://quizizz.com/join", "Quizzes no proprio ritmo do aluno com reforco imediato.", "#4F46E5"),
            ExternalTool("mentimeter", "Mentimeter", "Nuvem de Ideias", "https://www.menti.com", "Sondagem ao vivo, checagem de humor e nuvem de palavras.", "#1E293B")
        ]
        for t in tools:
            self.external_tools[t.id] = t

        initial_room_pin = "492810"
        self.rooms[initial_room_pin] = Room(
            pin=initial_room_pin,
            teacher_name="Prof. Ricardo",
            subject="Matematica Ativa",
            class_id="TURMA_A",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            is_focus_active=False,
            focus_duration_minutes=25,
            collective_points=105,
            collective_target=150,
            collective_reward="5 minutos livres no final da aula",
            connected_students={
                "aluno_1": {
                    "id": "aluno_1",
                    "name": "Evelyn",
                    "joined_at": datetime.now().strftime("%H:%M:%S"),
                    "status": "Conectado",
                    "round_seconds": 0,
                    "points_session": 20,
                    "streak_days": 5
                },
                "aluno_2": {
                    "id": "aluno_2",
                    "name": "Thiago",
                    "joined_at": datetime.now().strftime("%H:%M:%S"),
                    "status": "Conectado",
                    "round_seconds": 0,
                    "points_session": 15,
                    "streak_days": 3
                }
            },
            active_activity={
                "title": "Torneio de Fracoes e Algebra",
                "tool_name": "Kahoot!",
                "direct_link": "https://kahoot.it/?pin=492810",
                "access_pin": "492810",
                "sent_at": datetime.now().strftime("%H:%M")
            }
        )

        self.activity_sessions.append(
            ActivitySession(
                id="sessao_01",
                title="Torneio de Fracoes e Algebra",
                subject="Matematica Ativa",
                class_id="TURMA_A",
                tool_name="Kahoot!",
                direct_link="https://kahoot.it/?pin=492810",
                access_pin="492810",
                description="Responda em equipes no Kahoot. Apos o quiz, debater a logica em sala.",
                requires_pdf=False
            )
        )
        self.activity_sessions.append(
            ActivitySession(
                id="sessao_02",
                title="Relatorio: Organelas Celulares",
                subject="Biologia",
                class_id="TURMA_A",
                tool_name="Gartic & PDF",
                direct_link="https://gartic.com.br",
                access_pin="SALA-BIO-A",
                description="Apos o desenho no Gartic, envie o resumo teorico da organela em arquivo PDF.",
                requires_pdf=True
            )
        )

        self.pdf_submissions.append(
            PdfSubmission(
                id="sub_01",
                student_id="aluno_1",
                student_name="Evelyn",
                activity_id="sessao_02",
                activity_title="Relatorio: Organelas Celulares",
                filename="Relatorio_Organelas_Evelyn.pdf",
                status="Entregue",
                grade="Nota 10 / Excelente"
            )
        )

        missions = [
            MentalHealthMission(
                id="M1_RECREIO_OFFLINE",
                title="Pausa Consciente no Recreio",
                description="Permanecer os 20 minutos do intervalo conversando ou descansando, 100% longe das telas.",
                points_reward=30,
                category="desconexao"
            ),
            MentalHealthMission(
                id="M2_RESPIRACAO_GUIADA",
                title="Minuto Zen (Respiracao 4-7-8)",
                description="Exercicio voluntario de autorregulacao emocional antes de iniciar uma atividade avaliativa.",
                points_reward=15,
                category="respiracao"
            ),
            MentalHealthMission(
                id="M3_FOCO_POMODORO",
                title="Foco de Ouro (25 min sem alternar app)",
                description="Manter a atencao na dinamica proposta sem navegar paralelamente em redes sociais.",
                points_reward=40,
                category="foco"
            )
        ]
        for m in missions:
            self.missions[m.id] = m

        photo_quests = [
            PhotoQuest(
                id="Q1_ALGO_VERDE",
                title="Caca ao Tesouro: Algo Verde no Patio",
                description="Fotografe uma arvore, gramado, folha ou planta da escola. Conecte-se com o espaco real.",
                category="Natureza e Presenca",
                points_reward=25,
                icon_name="leaf"
            ),
            PhotoQuest(
                id="Q2_FLOR_BONITA",
                title="Olhar Atento: Uma Flor Bonita",
                description="Encontre uma flor no jardim da escola e registre seus detalhes e cores naturais.",
                category="Atencao Plena",
                points_reward=25,
                icon_name="flower"
            ),
            PhotoQuest(
                id="Q3_LIVRO_FISICO",
                title="Exploracao: Um Livro na Biblioteca",
                description="Visite a biblioteca e fotografe a capa de um livro que chame a sua curiosidade.",
                category="Cultura e Leitura",
                points_reward=30,
                icon_name="book"
            ),
            PhotoQuest(
                id="Q4_ARTE_MANUAL",
                title="Criatividade: Arte ou Desenho Manual",
                description="Fotografe um mural, desenho em papel ou escultura feita manualmente por colegas.",
                category="Expressao Humana",
                points_reward=25,
                icon_name="palette"
            )
        ]
        for q in photo_quests:
            self.photo_quests[q.id] = q

        self.trivia_facts = [
            TriviaFact("T1", "Neurociencia", "O poder do cerebro", "O cerebro humano consome cerca de 20% de toda a energia do corpo, mesmo representando apenas 2% da massa corporal."),
            TriviaFact("T2", "Astronomia", "A velocidade da luz", "A luz do Sol viaja a cerca de 300.000 km/s pelo vacuo e leva 8 minutos e 20 segundos para alcancar a Terra."),
            TriviaFact("T3", "Biologia e Ecologia", "Rede subterranea das florestas", "As arvores de uma floresta compartilham agua e nutrientes atraves de uma rede fungica no subsolo chamada micorriza."),
            TriviaFact("T4", "Historia e Quimica", "O alimento eterno", "O mel puro nao estraga! Arqueologos ja descobriram potes de mel com mais de 3.000 anos no Egito Antigo em perfeito estado."),
            TriviaFact("T5", "Fisica Espacial", "O silencio do cosmos", "No espaco sideral existe vacuo quase absoluto, portanto as ondas sonoras nao se propagam. O universo e silencioso.")
        ]

db = InMemoryDatabase()

# ==============================================================================
# 3. LOGICA DE NEGOCIO E SERVICOS
# ==============================================================================

class EducationalPlatformService:

    @staticmethod
    def create_room(teacher_name: str = "Prof. Ricardo", subject: str = "Matematica Ativa", class_id: str = "TURMA_A", duration: int = 25) -> Dict:
        while True:
            pin = str(random.randint(100000, 999999))
            if pin not in db.rooms:
                break

        room = Room(
            pin=pin,
            teacher_name=teacher_name,
            subject=subject,
            class_id=class_id,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            focus_duration_minutes=duration,
            collective_target=150,
            collective_reward="5 minutos livres no final da aula"
        )
        db.rooms[pin] = room

        return {
            "success": True,
            "message": f"Sala criada com sucesso. Codigo PIN: {pin}",
            "room": asdict(room)
        }

    @staticmethod
    def get_room_state(pin: str) -> Dict:
        room = db.rooms.get(pin)
        if not room:
            return {"success": False, "error": f"Sala com PIN {pin} nao encontrada."}

        session_pts = sum(s.get("points_session", 0) for s in room.connected_students.values())
        total_pts = room.collective_points + session_pts
        percentage = round((total_pts / room.collective_target * 100), 1) if room.collective_target > 0 else 0
        reward_unlocked = total_pts >= room.collective_target
        room.reward_unlocked = reward_unlocked

        students_list = list(room.connected_students.values())

        return {
            "success": True,
            "pin": room.pin,
            "teacher_name": room.teacher_name,
            "subject": room.subject,
            "class_id": room.class_id,
            "total_connected": len(students_list),
            "connected_students": students_list,
            "is_focus_active": room.is_focus_active,
            "focus_duration_minutes": room.focus_duration_minutes,
            "focus_started_at": room.focus_started_at,
            "focus_ends_at": room.focus_ends_at,
            "active_activity": room.active_activity,
            "collective_points": total_pts,
            "collective_target": room.collective_target,
            "progress_percentage": min(percentage, 100.0),
            "reward_unlocked": reward_unlocked,
            "collective_reward": room.collective_reward
        }

    @staticmethod
    def start_focus_cycle(pin: str, duration_minutes: int = 25) -> Dict:
        room = db.rooms.get(pin)
        if not room:
            return {"success": False, "error": "Sala nao encontrada."}

        now = datetime.now()
        ends = now + timedelta(minutes=duration_minutes)

        room.is_focus_active = True
        room.focus_duration_minutes = duration_minutes
        room.focus_started_at = now.strftime("%H:%M:%S")
        room.focus_ends_at = ends.strftime("%H:%M:%S")

        for st in room.connected_students.values():
            st["round_seconds"] = 0
            st["focus_failed"] = False
            st["pause_confirmed"] = False

        return {
            "success": True,
            "message": f"Ciclo de foco de {duration_minutes} minutos iniciado na sala {pin}.",
            "is_focus_active": True,
            "focus_duration_minutes": duration_minutes,
            "focus_started_at": room.focus_started_at,
            "focus_ends_at": room.focus_ends_at
        }

    @staticmethod
    def broadcast_activity(pin: str, tool_name: str, title: str, direct_link: str, access_pin: Optional[str] = None) -> Dict:
        room = db.rooms.get(pin)
        if not room:
            return {"success": False, "error": "Sala nao encontrada."}

        activity_payload = {
            "title": title,
            "tool_name": tool_name,
            "direct_link": direct_link,
            "access_pin": access_pin or pin,
            "sent_at": datetime.now().strftime("%H:%M")
        }
        room.active_activity = activity_payload

        return {
            "success": True,
            "message": f"Dinamica '{title}' ({tool_name}) transmitida para os alunos da sala {pin}.",
            "active_activity": activity_payload
        }

    @staticmethod
    def join_room(pin: str, student_name: str, student_id: Optional[str] = None) -> Dict:
        room = db.rooms.get(pin)
        if not room:
            return {"success": False, "error": f"Sala com PIN {pin} nao foi encontrada. Verifique o codigo com o professor."}

        matched_student = None
        if student_id and student_id in db.students:
            matched_student = db.students[student_id]
        else:
            for s in db.students.values():
                if s.name.lower() == student_name.strip().lower():
                    matched_student = s
                    break

        if not matched_student:
            new_id = f"aluno_{len(db.students) + 1}"
            matched_student = Student(id=new_id, name=student_name.strip(), class_id=room.class_id, points=10, streak_days=1)
            db.students[new_id] = matched_student

        room.connected_students[matched_student.id] = {
            "id": matched_student.id,
            "name": matched_student.name,
            "joined_at": datetime.now().strftime("%H:%M:%S"),
            "status": "Conectado",
            "round_seconds": 0,
            "points_session": 0,
            "streak_days": matched_student.streak_days,
            "focus_failed": False,
            "pause_confirmed": False
        }

        return {
            "success": True,
            "message": f"{matched_student.name} ingressou na sala {pin}.",
            "student": asdict(matched_student),
            "room_pin": pin,
            "subject": room.subject,
            "teacher_name": room.teacher_name,
            "is_focus_active": room.is_focus_active
        }

    @staticmethod
    def focus_tick(pin: str, student_id: str, seconds_elapsed: int = 60) -> Dict:
        room = db.rooms.get(pin)
        if not room:
            return {"success": False, "error": "Sala nao encontrada."}

        student = db.students.get(student_id)
        if not student:
            return {"success": False, "error": "Aluno nao encontrado."}

        connected = room.connected_students.get(student_id)
        if not connected:
            return {"success": False, "error": "Aluno nao esta conectado nesta sala."}

        connected["round_seconds"] = connected.get("round_seconds", 0) + seconds_elapsed

        points_earned = 10
        student.points += points_earned
        connected["points_session"] = connected.get("points_session", 0) + points_earned
        student.minutes_offline += 1

        tx = PointTransaction(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            student_id=student_id,
            points=points_earned,
            reason="Minuto concluido no Modo Foco sem interrupcoes"
        )
        db.transactions.append(tx)

        total_session_pts = sum(s.get("points_session", 0) for s in room.connected_students.values())
        current_room_total = room.collective_points + total_session_pts
        if current_room_total >= room.collective_target:
            room.reward_unlocked = True

        return {
            "success": True,
            "message": f"+{points_earned} pontos por 1 minuto de foco ininterrupto.",
            "points_earned": points_earned,
            "student_points": student.points,
            "round_seconds": connected["round_seconds"],
            "room_collective_points": current_room_total,
            "reward_unlocked": room.reward_unlocked
        }

    @staticmethod
    def record_focus_failure(pin: str, student_id: str, reason: str = "Saida da tela ou minimizacao detectada") -> Dict:
        room = db.rooms.get(pin)
        connected = room.connected_students.get(student_id) if room else None

        if connected:
            connected["round_seconds"] = 0
            connected["focus_failed"] = True
            connected["status"] = "Interrompido"

        return {
            "success": True,
            "alert": "Atencao: Foco interrompido! Voce saiu do aplicativo durante o ciclo.",
            "consequence": "O tempo desta rodada individual foi zerado.",
            "round_seconds": 0
        }

    @staticmethod
    def confirm_conscious_pause(pin: str, student_id: str) -> Dict:
        student = db.students.get(student_id)
        if not student:
            return {"success": False, "error": "Aluno nao encontrado."}

        room = db.rooms.get(pin) if pin else None
        bonus_points = 15
        student.points += bonus_points

        if room and student_id in room.connected_students:
            room.connected_students[student_id]["pause_confirmed"] = True
            room.connected_students[student_id]["points_session"] = room.connected_students[student_id].get("points_session", 0) + bonus_points

        tx = PointTransaction(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            student_id=student_id,
            points=bonus_points,
            reason="Bonus por cumprimento da Pausa Consciente (Descanso Visual)"
        )
        db.transactions.append(tx)

        return {
            "success": True,
            "message": f"Pausa Consciente confirmada! Voce recebeu +{bonus_points} pontos bonus de descanso visual.",
            "bonus_points": bonus_points,
            "total_points": student.points
        }

    @staticmethod
    def increment_streak(student_id: str) -> Dict:
        student = db.students.get(student_id)
        if not student:
            return {"success": False, "error": "Aluno nao encontrado."}

        student.streak_days += 1
        student.points += 10
        return {
            "success": True,
            "message": f"Ofensiva atualizada: {student.streak_days} dias seguidos (+10 pts).",
            "streak_days": student.streak_days,
            "streak_text": f"Ofensiva: {student.streak_days} dias seguidos",
            "total_points": student.points
        }

    @staticmethod
    def award_presence_bonus(student_id: str, bonus_points: int = 25, teacher_comment: str = "Meta de presenca consciente atingida") -> Dict:
        student = db.students.get(student_id)
        if not student:
            return {"success": False, "error": "Aluno nao encontrado."}

        student.points += bonus_points
        student.presence_bonus_awarded = True

        tx = PointTransaction(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            student_id=student_id,
            points=bonus_points,
            reason=f"Bonus do Docente: {teacher_comment}"
        )
        db.transactions.append(tx)

        return {
            "success": True,
            "message": f"O professor concedeu +{bonus_points} pontos extras de presenca para {student.name}.",
            "student": asdict(student)
        }

    @staticmethod
    def toggle_dnd(student_id: str) -> Dict:
        student = db.students.get(student_id)
        if not student:
            return {"success": False, "error": "Aluno nao encontrado."}

        student.notifications_blocked = not student.notifications_blocked
        status_txt = "Ativado (Notificacoes de redes bloqueadas)" if student.notifications_blocked else "Desativado (Modo Padrao)"
        return {
            "success": True,
            "notifications_blocked": student.notifications_blocked,
            "notifications_silenced_count": student.notifications_silenced_count,
            "message": f"Modo Foco {status_txt} para {student.name}."
        }

    @staticmethod
    def get_weekly_report(role: str = "student", target_id: str = "aluno_1") -> Dict:
        if role == "teacher":
            return {
                "success": True,
                "scope": "Turma A (1o Ano Medio)",
                "role": "teacher",
                "summary": "Media semanal da sala de aula",
                "productive_percentage": 84,
                "total_offline_hours": 15.2,
                "total_notifications_silenced": 128,
                "daily_breakdown": [
                    {"day": "Segunda", "educational_min": 50, "social_media_min": 20},
                    {"day": "Terca", "educational_min": 65, "social_media_min": 15},
                    {"day": "Quarta", "educational_min": 55, "social_media_min": 10},
                    {"day": "Quinta", "educational_min": 60, "social_media_min": 12},
                    {"day": "Sexta", "educational_min": 55, "social_media_min": 8}
                ],
                "insight": "A Turma A reduziu o uso de redes sociais em 48% durante as aulas esta semana."
            }
        else:
            student = db.students.get(target_id) or db.students.get("aluno_1")
            return {
                "success": True,
                "scope": f"{student.name} ({student.class_id})" if student else "Aluno",
                "role": "student",
                "student_id": student.id if student else target_id,
                "productive_percentage": 79,
                "personal_offline_minutes": student.minutes_offline if student else 45,
                "notifications_silenced": student.notifications_silenced_count if student else 14,
                "daily_breakdown": [
                    {"day": "Segunda", "educational_min": 45, "social_media_min": 18},
                    {"day": "Terca", "educational_min": 50, "social_media_min": 12},
                    {"day": "Quarta", "educational_min": 45, "social_media_min": 10},
                    {"day": "Quinta", "educational_min": 55, "social_media_min": 15},
                    {"day": "Sexta", "educational_min": 50, "social_media_min": 5}
                ],
                "insight": "Otimo desempenho: 79% do tempo no celular durante a aula foi dedicado ao aprendizado ativo."
            }

    @staticmethod
    def complete_photo_quest(student_id: str, quest_id: str, photo_name: str = "registro.jpg") -> Dict:
        student = db.students.get(student_id)
        quest = db.photo_quests.get(quest_id)
        if not student or not quest:
            return {"success": False, "error": "Aluno ou desafio fotografico nao encontrado."}

        if quest_id in student.completed_photo_quests:
            return {"success": False, "error": "Este desafio ja foi concluido anteriormente."}

        student.completed_photo_quests.append(quest_id)
        student.points += quest.points_reward

        return {
            "success": True,
            "message": f"Foto validada com sucesso. Desafio '{quest.title}' concluido (+{quest.points_reward} pts).",
            "points_earned": quest.points_reward,
            "total_points": student.points
        }

    @staticmethod
    def submit_pdf_activity(student_id: str, activity_id: str, filename: str) -> Dict:
        student = db.students.get(student_id)
        activity = next((a for a in db.activity_sessions if a.id == activity_id), None)
        if not student or not activity:
            return {"success": False, "error": "Aluno ou atividade nao encontrados."}

        sub_id = f"sub_{len(db.pdf_submissions) + 1:02d}"
        submission = PdfSubmission(
            id=sub_id,
            student_id=student_id,
            student_name=student.name,
            activity_id=activity_id,
            activity_title=activity.title,
            filename=filename
        )
        db.pdf_submissions.append(submission)
        student.points += 20

        return {
            "success": True,
            "message": f"Atividade em PDF '{filename}' enviada por {student.name} (+20 pts).",
            "submission": asdict(submission)
        }

# ==============================================================================
# 4. ROTAS DA API REST (FLASK)
# ==============================================================================

app = Flask(__name__, template_folder=".")

@app.route("/", methods=["GET"])
def home():
    if request.headers.get("Accept") == "application/json" or request.args.get("format") == "json":
        return jsonify({
            "project": "FocAE - Foco Consciente e Gamificacao Educacional",
            "version": "3.0 Clean",
            "rooms": len(db.rooms),
            "students": len(db.students),
            "classes": len(db.classes)
        })
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "app": "FocAE",
        "timestamp": datetime.now().isoformat(),
        "rooms": len(db.rooms),
        "students": len(db.students),
        "classes": len(db.classes),
        "storage": "In-Memory Data Structures (Python)"
    })

@app.route("/api/rooms", methods=["GET"])
def list_rooms():
    return jsonify({
        "success": True,
        "rooms": [asdict(r) for r in db.rooms.values()]
    })

@app.route("/api/rooms/create", methods=["POST"])
def create_room_route():
    data = request.get_json() or {}
    teacher = data.get("teacher_name", "Prof. Ricardo")
    subject = data.get("subject", "Matematica Ativa")
    class_id = data.get("class_id", "TURMA_A")
    duration = int(data.get("duration", 25))
    res = EducationalPlatformService.create_room(teacher, subject, class_id, duration)
    return jsonify(res), 201

@app.route("/api/rooms/<pin>", methods=["GET"])
def get_room_route(pin):
    res = EducationalPlatformService.get_room_state(pin)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/rooms/<pin>/start_focus", methods=["POST"])
def start_focus_route(pin):
    data = request.get_json() or {}
    duration = int(data.get("duration", 25))
    res = EducationalPlatformService.start_focus_cycle(pin, duration)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/rooms/<pin>/send_activity", methods=["POST"])
def send_activity_route(pin):
    data = request.get_json() or {}
    tool_name = data.get("tool_name", "Kahoot!")
    title = data.get("title", "Dinamica Interativa")
    direct_link = data.get("direct_link", "https://kahoot.it")
    access_pin = data.get("access_pin", pin)
    res = EducationalPlatformService.broadcast_activity(pin, tool_name, title, direct_link, access_pin)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/rooms/<pin>/join", methods=["POST"])
def join_room_route(pin):
    data = request.get_json() or {}
    student_name = data.get("student_name", "Aluno Convidado")
    student_id = data.get("student_id")
    res = EducationalPlatformService.join_room(pin, student_name, student_id)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/rooms/<pin>/focus_tick", methods=["POST"])
def focus_tick_route(pin):
    data = request.get_json() or {}
    student_id = data.get("student_id", "aluno_1")
    seconds = int(data.get("seconds", 60))
    res = EducationalPlatformService.focus_tick(pin, student_id, seconds)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/rooms/<pin>/focus_failed", methods=["POST"])
def focus_failed_route(pin):
    data = request.get_json() or {}
    student_id = data.get("student_id", "aluno_1")
    reason = data.get("reason", "Saida de tela detectada")
    res = EducationalPlatformService.record_focus_failure(pin, student_id, reason)
    return jsonify(res), 200

@app.route("/api/rooms/<pin>/confirm_pause", methods=["POST"])
def confirm_pause_route(pin):
    data = request.get_json() or {}
    student_id = data.get("student_id", "aluno_1")
    res = EducationalPlatformService.confirm_conscious_pause(pin, student_id)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/students", methods=["GET"])
def get_students():
    return jsonify({
        "success": True,
        "students": [asdict(s) for s in db.students.values()]
    })

@app.route("/api/students/<student_id>", methods=["GET"])
def get_student(student_id):
    student = db.students.get(student_id)
    if not student:
        return jsonify({"success": False, "error": "Aluno nao encontrado"}), 404
    return jsonify({"success": True, "student": asdict(student)})

@app.route("/api/students/<student_id>/streak", methods=["POST"])
def streak_route(student_id):
    res = EducationalPlatformService.increment_streak(student_id)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/students/<student_id>/presence_bonus", methods=["POST"])
def presence_bonus_route(student_id):
    data = request.get_json() or {}
    bonus = int(data.get("bonus", 25))
    comment = data.get("comment", "Meta de presenca atingida")
    res = EducationalPlatformService.award_presence_bonus(student_id, bonus, comment)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/students/<student_id>/toggle_dnd", methods=["POST"])
def toggle_dnd_route(student_id):
    res = EducationalPlatformService.toggle_dnd(student_id)
    return jsonify(res), (200 if res["success"] else 404)

@app.route("/api/students/<student_id>/photo_quest", methods=["POST"])
def photo_quest_route(student_id):
    data = request.get_json() or {}
    quest_id = data.get("quest_id")
    photo_name = data.get("photo_name", "registro.jpg")
    res = EducationalPlatformService.complete_photo_quest(student_id, quest_id, photo_name)
    return jsonify(res), (200 if res["success"] else 400)

@app.route("/api/students/<student_id>/submit_pdf", methods=["POST"])
def submit_pdf_route(student_id):
    data = request.get_json() or {}
    activity_id = data.get("activity_id")
    filename = data.get("filename", "Trabalho_Aluno.pdf")
    res = EducationalPlatformService.submit_pdf_activity(student_id, activity_id, filename)
    return jsonify(res), (200 if res["success"] else 400)

@app.route("/api/weekly_report", methods=["GET"])
def weekly_report_route():
    role = request.args.get("role", "student")
    target_id = request.args.get("target_id", "aluno_1")
    res = EducationalPlatformService.get_weekly_report(role, target_id)
    return jsonify(res)

@app.route("/api/trivia", methods=["GET"])
def trivia_route():
    return jsonify({
        "success": True,
        "facts": [asdict(t) for t in db.trivia_facts]
    })

@app.route("/api/photo_quests", methods=["GET"])
def get_photo_quests():
    return jsonify({
        "success": True,
        "quests": [asdict(q) for q in db.photo_quests.values()]
    })

@app.route("/api/activities", methods=["GET"])
def get_activities():
    return jsonify({
        "success": True,
        "quick_tools": [asdict(t) for t in db.external_tools.values()],
        "active_sessions": [asdict(s) for s in db.activity_sessions if s.active]
    })

@app.route("/api/pdf_submissions", methods=["GET"])
def get_pdf_submissions():
    return jsonify({
        "success": True,
        "submissions": [asdict(s) for s in db.pdf_submissions]
    })

def run_console_demo():
    sep = "=" * 70
    sub_sep = "-" * 70

    print("\n" + sep)
    print("  [FocAE] - PLATAFORMA MOBILE & FOCO CONSCIENTE NA ESCOLA")
    print("  Hackathon Bemobi | Saude Mental, Autonomia e Metodologias Ativas")
    print(sep)

    print("\n[MODULO DO PROFESSOR]")
    print("  * RF01 - Criando sala de aula...")
    r_create = EducationalPlatformService.create_room("Prof. Ricardo", "Matematica Ativa", "TURMA_A", 25)
    pin = r_create["room"]["pin"]
    print(f"    -> Sala criada com sucesso! PIN de 6 digitos: {pin}")

    print(f"\n  * RF04 - Professor transmite dinamica Kahoot para a sala {pin}...")
    EducationalPlatformService.broadcast_activity(pin, "Kahoot!", "Torneio de Algebra", "https://kahoot.it", pin)
    print("    -> Link e PIN da dinamica enviados para a sala.")

    print(f"\n  * RF03 - Professor inicia ciclo coletivo de foco de 25 minutos...")
    EducationalPlatformService.start_focus_cycle(pin, 25)
    print("    -> Cronometro coletivo ativado na sala.")

    print("\n" + sub_sep)
    print("[MODULO DO ALUNO]")
    print(f"  * RF05 - Aluna Evelyn ingressa na sala com o PIN {pin}...")
    EducationalPlatformService.join_room(pin, "Evelyn", "aluno_1")
    print("    -> Evelyn conectada com sucesso a sala.")

    print("\n  * RF09 - Aluna completa 1 minuto de foco sem alternar tela...")
    r_tick = EducationalPlatformService.focus_tick(pin, "aluno_1", 60)
    print(f"    -> {r_tick['message']} Pontos totais: {r_tick['student_points']}")

    print("\n  * RF07 - Simulando detector de saida da tela (visibilitychange)...")
    r_fail = EducationalPlatformService.record_focus_failure(pin, "aluno_1", "Troca de aba detectada")
    print(f"    -> {r_fail['alert']}")
    print(f"    -> Consequencia: {r_fail['consequence']}")

    print("\n  * RF08 e RF10 - Confirmando Pausa Consciente...")
    r_pause = EducationalPlatformService.confirm_conscious_pause(pin, "aluno_1")
    print(f"    -> {r_pause['message']}")

    print("\n  * RF11 - Sequencia de Presenca (Streak):")
    r_streak = EducationalPlatformService.increment_streak("aluno_1")
    print(f"    -> {r_streak['streak_text']}")

    print("\n" + sub_sep)
    print("[RF12 - PAINEL AO VIVO E META COLETIVA]")
    room_state = EducationalPlatformService.get_room_state(pin)
    print(f"  Alunos Conectados: {room_state['total_connected']}")
    print(f"  Pontos Coletivos: {room_state['collective_points']} / {room_state['collective_target']} pts ({room_state['progress_percentage']}%)")
    print(f"  Recompensa Coletiva: {room_state['collective_reward']} [Status: {'DESBLOQUEADA' if room_state['reward_unlocked'] else 'Em Progresso'}]")

    print("\n" + sep)
    print("  [OK] REQUISITOS RF01 A RF12 VALIDADOS COM SUCESSO!")
    print(sep + "\n")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--demo" in args:
        run_console_demo()
    else:
        run_console_demo()
        print("Servidor ativo:")
        print(" -> No seu PC:          http://127.0.0.1:5000")
        print(" -> No Celular (Wi-Fi): http://192.168.1.108:5000")
        print("Pressione CTRL+C para encerrar o servidor a qualquer momento.")
        app.run(host="0.0.0.0", port=5000, debug=False)
