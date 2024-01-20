jtype_texts = {
    "tl": "translated",
    "pr": "pred",
    "cln": "cleaned",
    "ts": "tsed"
}


class Jobs:
    def __init__(self, series: dict):
        self.series = series

        self.tls = self.__get_all_personnel_ids("tl")
        self.prs = self.__get_all_personnel_ids("pr")
        self.clnrs = self.__get_all_personnel_ids("clnr")
        self.tsers = self.__get_all_personnel_ids("tser")

        self.tl_jobs = self.__get_normal_jobs("tl")
        self.pr_jobs = self.__get_normal_jobs("pr")
        self.clnr_jobs = self.__get_normal_jobs("cln")
        self.tser_jobs = self.__get_normal_jobs("ts")

    class Job:
        def __init__(self, jtype: str, jid: int, jname: str, pid: int, schap: float, echap: float):
            self.jtype = jtype
            self.jid = jid
            self.jname = jname
            self.pid = pid
            self.schap = schap
            self.echap = echap

        def __repr__(self):
            return f"Job(<{self.jname}>, <{self.pid}>, <{self.schap}>, <{self.echap}>)"

        def __str__(self):
            return f"{self.jname} -->    ***Last {jtype_texts[self.jtype]}:*** *{self.schap}*    ***Waiting for:*** *{self.echap}*"

    def __get_all_personnel_ids(self, personnel_type: str) -> list:
        return list(set([serie[personnel_type] for serie in self.series if len(str(serie[personnel_type])) != 1]))

    def __get_normal_jobs(self, jtype: str) -> list:
        jobs = []
        if jtype == "tl":
            for serie in self.series:
                if len(str(serie["pr"])) > 1:
                    if serie["source_chap"] > serie["waiting_pr"]:
                        jobs.append(
                            self.Job(
                                "tl",
                                serie["id"],
                                serie["name"],
                                serie["tl"],
                                serie["waiting_pr"],
                                serie["source_chap"]
                            )
                        )
                else:
                    if serie["source_chap"] > serie["pred"]:
                        jobs.append(
                            self.Job(
                                "tl",
                                serie["id"],
                                serie["name"],
                                serie["tl"],
                                serie["pred"],
                                serie["source_chap"]
                            )
                        )
        elif jtype == "pr":
            for serie in self.series:
                if len(str(serie["pr"])) > 1:
                    if serie["waiting_pr"] > serie["pred"]:
                        jobs.append(
                            self.Job(
                                "pr",
                                serie["id"],
                                serie["name"],
                                serie["pr"],
                                serie["pred"],
                                serie["waiting_pr"]
                            )
                        )
        elif jtype == "cln":
            for serie in self.series:
                if len(str(serie["clnr"])) > 1:
                    if serie["source_chap"] > serie["cleaned"]:
                        jobs.append(
                            self.Job(
                                "cln",
                                serie["id"],
                                serie["name"],
                                serie["clnr"],
                                serie["cleaned"],
                                serie["source_chap"]
                            )
                        )
        elif jtype == "ts":
            for serie in self.series:
                if len(str(serie["clnr"])) > 1:
                    if serie["cleaned"] > serie["completed"] and serie["pred"] > serie["completed"]:
                        jobs.append(
                            self.Job(
                                "ts",
                                serie["id"],
                                serie["name"],
                                serie["tser"],
                                serie["completed"],
                                serie["pred"]
                            )
                        )
                else:
                    if serie["pred"] > serie["completed"]:
                        jobs.append(
                            self.Job(
                                "ts",
                                serie["id"],
                                serie["name"],
                                serie["tser"],
                                serie["completed"],
                                serie["pred"]
                            )
                        )

        return jobs

    def __get_tl_jobs(self):
        tl_dict = {}
        for tl in self.tls:
            tl_dict[tl] = []

            for job in self.tl_jobs:
                if job.pid == tl:
                    tl_dict[tl].append(job)

        return tl_dict

    def __get_pr_jobs(self):
        pr_dict = {}
        for pr in self.prs:
            pr_dict[pr] = []

            for job in self.pr_jobs:
                if job.pid == pr:
                    pr_dict[pr].append(job)

        return pr_dict
    
    def __get_clnr_jobs(self):
        clnr_dict = {}
        for clnr in self.clnrs:
            clnr_dict[clnr] = []

            for job in self.clnr_jobs:
                if job.pid == clnr:
                    clnr_dict[clnr].append(job)

        return clnr_dict
    
    def __get_tser_jobs(self):
        tser_dict = {}
        for tser in self.tsers:
            tser_dict[tser] = []

            for job in self.tser_jobs:
                if job.pid == tser:
                    tser_dict[tser].append(job)

        return tser_dict
    
    def create_main_text(self, jtype: str):
        jobs = {}
        if jtype == "tl":
            jobs = self.__get_tl_jobs()
        elif jtype == "pr":
            jobs = self.__get_pr_jobs()
        elif jtype == "clnr":
            jobs = self.__get_clnr_jobs()
        elif jtype == "tser":
            jobs = self.__get_tser_jobs()

        text = ""

        for key, value in jobs.items():
            text += f"<@{key}>\n"
            for job in value:
                text += str(job)
                text += "\n"

            text += "\n"

        return text

    @staticmethod
    def split_daily_text(text: str):
        splitted = text.split("\n\n")
        minl = 1000
        sections = []
        section = []

        for part in splitted:
            newl = len("\n\n".join(section) + f"{part}\n\n")
            if newl < minl or minl == newl:
                section.append(part)
            else:
                section.append(f"{part}\n\n")
                sections.append(section)
                section = []

        if section:
            sections.append(section)

        return sections
