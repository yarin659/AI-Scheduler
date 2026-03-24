class ComparativeExplainer:
    @staticmethod
    def explain(best, alternatives):
        reasons = []

        for alt in alternatives:
            if best["features"]["hour"] != alt["features"]["hour"]:
                reasons.append(
                    f"Chosen hour {best['features']['hour']}:00 "
                    f"over {alt['features']['hour']}:00 "
                    f"based on your past preferences"
                )

            if best["features"]["task_category"] != alt["features"]["task_category"]:
                reasons.append(
                    f"Preferred {best['features']['task_category']} "
                    f"tasks at this time"
                )
            if not reasons:
                reasons.append(
                    "This time fits your general scheduling preferences"
                )

        return list(dict.fromkeys(reasons))  # remove duplicates
