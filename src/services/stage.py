from typing import Any
from colorama import Style, Fore
import models.game
import network

_DIFFICULTIES = ['Normal', 'Very Hard', 'Super Hard 1', 'Super Hard 2', 'Super Hard 3']


class StageService:
    @staticmethod
    def get_friend(stage_id: int, difficulty: int):
        """Fetch supporter or CPU friend safely for a given stage."""
        if difficulty < 0 or difficulty >= len(_DIFFICULTIES):
            print(f"[StageService] ⚠️ Invalid difficulty index: {difficulty}. Valid range: 0-{len(_DIFFICULTIES)-1}")
            difficulty_name = f"Unknown({difficulty})"
        else:
            difficulty_name = _DIFFICULTIES[difficulty]

        print(f"[StageService] Fetching supporters for stage {stage_id} ({difficulty_name})...")
        r = network.get_quests_supporters(stage_id=stage_id, difficulty=difficulty, team_num=1)

        if not isinstance(r, dict):
    
            print("[DEBUG supporters]", r)

            return None
        if "error" in r:
        
            return None

        if "cpu_supporters" in r:
            difficulty_key = _DIFFICULTIES[difficulty].lower().replace(" ", "_")
            if difficulty_key in r["cpu_supporters"]:
                cpu_friends = r["cpu_supporters"][difficulty_key].get("cpu_friends", [])
                if cpu_friends:
                    print(f"[StageService] ✅ Using CPU supporter (difficulty: {difficulty_name})")
                    return {
                        "is_cpu": True,
                        "id": cpu_friends[0]["id"],
                        "leader": cpu_friends[0]["card_id"],
                    }

        if "supporters" not in r or not r["supporters"]:
            print(f"[StageService] ⚠️ No supporters found for stage {stage_id} ({difficulty_name})")
            return None

        supporter = r["supporters"][0]


        return {
            "is_cpu": False,
            
            "id": supporter.get("id"),
            "leader": supporter.get("leader"),
        }

    # ✅ Add this new method to start quest safely
    @staticmethod
    def start_stage(stage_id: int, sign: Any):
        """Start quest with proper error handling."""
        res = network.post_quests_sugoroku_start(stage_id, sign)

        if isinstance(res, dict) and "error" in res:
            err = res["error"]
            err_code = err.get("code") if isinstance(err, dict) else str(err)
            

            if err_code == "invalid_token":
                print("[Stage] Token invalid — please re-login.")
                return {"error": err}
            elif err_code == "unavailable_quest":
                print(f"[Stage] ⚠️ Quest {stage_id} is unavailable — skipping.")
                return {"skip": "unavailable_quest"}
            else:
                print(f"[Stage] Unhandled error: {err_code}")
                return {"error": err}

        return res

    @staticmethod
    def get_sign(friend, kagi, difficulty: int, selected_team_num: int):
        """Generate the encrypted stage sign payload."""
        if not friend:
            print("[StageService] ❌ No valid friend found. Cannot build sign.")
            return None

        if not friend["is_cpu"]:
            payload = {
                "bgm_filename": "",
                "difficulty": difficulty,
                "friend_id": int(friend["id"]),
                "is_playing_script": True,
                "selected_team_num": selected_team_num,
                "support_leader": friend["leader"],
            }
            if kagi is not None:
                payload["eventkagi_item_id"] = kagi
        else:
            payload = {
                "difficulty": difficulty,
                "cpu_friend_id": int(friend["id"]),
                "is_playing_script": True,
                "selected_team_num": selected_team_num,
            }
            if kagi is not None:
                payload["eventkagi_item_id"] = kagi

        return payload

    @staticmethod
    def get_difficulty_name(difficulty: int) -> str:
        if 0 <= difficulty < len(_DIFFICULTIES):
            return _DIFFICULTIES[difficulty]
        return f"Unknown({difficulty})"

    @staticmethod
    def print_rewards(sign: Any):
        # (your reward printing code — unchanged)
        ...
