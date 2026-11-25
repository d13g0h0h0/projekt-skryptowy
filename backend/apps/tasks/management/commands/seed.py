from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.tasks.models import Task,SubTask
from apps.solutions.models import Solution, Vote, SolutionPart
TASKS = [
    {
        "title": "Równoległobok i równe kąty",
        "author": "AlicjaKotowska",
        "content": r"""Dany jest równoległobok \(ABCD\). Na odcinku \(CD\) leżą takie punkty \(X\) i \(Y\), że \(\angle XAB = \angle XAD\) oraz \(\angle YBA = \angle YBC\).

Wykaż, że \(CX = DY\).""",
        "solutions": [],
    },
    {
        "title": "Liczba o różnych cyfrach podzielna przez każdą z nich",
        "author": "HaniaZipser",
        "content": r"""W zapisie dziesiętnym dodatniej liczby całkowitej \(n\) każda cyfra jest różna od \(0\) oraz żadna cyfra nie pojawia się więcej niż raz. Ponadto liczba \(n\) jest podzielna przez każdą ze swoich cyfr.

Wykaż, że liczba \(n\) ma co najwyżej \(7\) cyfr.""",
        "solutions": [],
    },
    {
        "title": "Pionek na planszy 1×100",
        "author": "AndrzejLas",
        "content": r"""Pola prostokątnej planszy \(1 \times 100\) są ponumerowane kolejno liczbami całkowitymi od \(1\) do \(100\). Pionek początkowo stał na polu o numerze \(n\). W pierwszym ruchu przesunięto go o jedno pole, w drugim - o dwa pola, w trzecim - o trzy pola itd. Okazało się, że po wykonaniu \(99\) ruchów pionek odwiedził każde pole dokładnie raz.

Wyznacz wszystkie możliwe wartości \(n\).

*Uwaga.* Przesunięcie pionka o \(k\) pól oznacza bezpośrednie przemieszczenie go między polami, których numery różnią się o \(k\).""",
        "solutions": [],
    },
    {
        "title": "Trapez i punkty P, Q na podstawach",
        "author": "AndrzejLas",
        "content": r"""Dany jest trapez \(ABCD\) o podstawach \(AB\) oraz \(CD\). Punkty \(P\) i \(Q\) leżą odpowiednio na odcinkach \(AB\) i \(CD\), przy czym \(AQ = BQ\) oraz \(CP = DP\).

Wykaż, że \(AP + DQ = BP + CQ\).""",
        "solutions": [],
    },
    {
        "title": "Język yonggom",
        "author": "AlicjaKotowska",
        "content": r"""Podane są zdania w języku yonggom i ich tłumaczenia na polski:

1. Meneni karuwa anona wedmaan. - Przyszedłem i zobaczyłem mężczyznę i psa.
2. Wingkeewa yeediriin. - Śpiewasz, a ja wstaję.
3. Ambib wedmoona awon baan. - Zobaczył dom, a ja wziąłem świnię.
4. Yeederenu om banuun. - Ona wstanie i weźmie chleb.
5. Wenenub wingkanuub. - Odejdziemy i zaśpiewamy.
6. Oma oka aniib. - Jedzą chleb i piją wodę.
7. Anon ye weng wengambaranuuwa awon ye weng wengambaraneen. - Usłyszymy psa, a on usłyszy świnię.
8. Ok anaana oon wedmeen. - Wypiłem wodę, a ona zobaczyła rybę.
9. Yeederenib miniib. - Wstają i przychodzą.
10. Wingkenu wunuun. - Ona śpiewa i odchodzi.
11. Om bene aneen. - On bierze chleb i zjada go.""",
        "subtasks": [
            r"""(a) Przetłumacz na polski:

12. Om benu aneen.
13. Munuuna wunuub.
14. Wingkiiwa wengamburuun.
15. Anon ye weng wengamberenib yeedaraniib.
16. Oon wedmaniina karub wedmaneeb.
17. Ok wedmeena aniin.""",
            r"""(b) Przetłumacz na język yonggom:

18. Odejdziemy, a oni przyjdą.
19. Biorę świnię, a on bierze rybę.
20. Zobaczył wodę i dom i usłyszał psa.
21. Jesz chleb i śpiewasz.""",
        ],
        "solutions": [
            {
                "author": "AndrzejLas",
                "content": r"""Rozwiązałem to, porównując końcówki czasowników w zdaniach 1-11. Końcówki zmieniają się w zależności od osoby i czasu, a spójnik „i” jest zaznaczony na czasowniku, a nie osobnym słowem.""",
                "parts": [
                    {"subtask": 1, "content": r"""12. On bierze chleb i zjada go.
13. Przychodzę, a oni odchodzą.
14. Śpiewacie, a on usłyszy psa.
15. Usłyszą psa, a on wstanie i przyjdzie.
16. Zobaczył rybę, a ja zobaczyłem mężczyznę.
17. Wypijesz wodę."""},
                    {"subtask": 2, "content": r"""18. Wenenuuwa miniib.
19. Baan awon ye weng bene oon.
20. Ok wedmoona ambib wedmaan anon wengambaraneen.
21. Om aneen wingkeewa."""},
                ],
                "votes": [
                    {"user": "HaniaZipser", "value": 1},
                    {"user": "AlicjaKotowska", "value": 1},
                ],
            },
        ],
    },
]

class Command(BaseCommand):
    help = "Seed tasks and solutions using existing users"

    @transaction.atomic
    def handle(self, *args, **opts):
        User = get_user_model()

        usernames = (
            {t["author"] for t in TASKS}
            | {s["author"] for t in TASKS for s in t["solutions"]}
            | {v["user"] for t in TASKS for s in t["solutions"] for v in s.get("votes", [])}
        )
        users = {u.username: u for u in User.objects.filter(username__in=usernames)}
        missing = usernames - users.keys()
        if missing:
            raise CommandError(f"No users in a database: {', '.join(sorted(missing))}")

        for t in TASKS:
            task, created = Task.objects.get_or_create(
                title=t["title"],
                author=users[t["author"]],
                defaults={"content": t["content"]},
            )
            if created:
                SubTask.objects.bulk_create([
                    SubTask(task=task, content=c, position=i)
                    for i, c in enumerate(t.get("subtasks", []), start=1)
                ])
            subtasks = {st.position: st for st in task.subtasks.all()}

            for s in t["solutions"]:
                solution, _ = Solution.objects.get_or_create(
                    task=task,
                    author=users[s["author"]],
                    defaults={"content": s.get("content", "")},
                )
                for p in s.get("parts", []):
                    SolutionPart.objects.get_or_create(
                        solution=solution,
                        subtask=subtasks[p["subtask"]],
                        defaults={"content": p["content"]},
                    )
                for v in s.get("votes", []):
                    Vote.objects.update_or_create(
                        solution=solution,
                        user=users[v["user"]],
                        defaults={"value": v["value"]},
                    )

        self.stdout.write(self.style.SUCCESS("Seed done"))