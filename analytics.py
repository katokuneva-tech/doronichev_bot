import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import config

class BotAnalytics:
    def __init__(self):
        self.analytics_file = config.ANALYTICS_FILE
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data["total_users"] = set(data.get("total_users", []))
                data["messages_by_date"] = defaultdict(int, data.get("messages_by_date", {}))
                data["user_messages"] = defaultdict(int, data.get("user_messages", {}))
                return data
        
        return {
            "total_users": set(),
            "total_messages": 0,
            "messages_by_date": defaultdict(int),
            "user_messages": defaultdict(int),
            "conversation_lengths": [],
            "queries": []
        }
    
    def save_data(self):
        data_to_save = self.data.copy()
        data_to_save["total_users"] = list(self.data["total_users"])
        data_to_save["messages_by_date"] = dict(self.data["messages_by_date"])
        data_to_save["user_messages"] = dict(self.data["user_messages"])
        
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    def log_message(self, user_id, message_text):
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.data["total_users"].add(user_id)
        self.data["total_messages"] += 1
        self.data["messages_by_date"][today] += 1
        self.data["user_messages"][str(user_id)] += 1
        self.data["queries"].append({
            "date": datetime.now().isoformat(),
            "user_id": user_id,
            "text": message_text[:100]
        })
        
        if len(self.data["queries"]) > 1000:
            self.data["queries"] = self.data["queries"][-1000:]
        
        self.save_data()
    
    def get_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        
        keywords = []
        for query in self.data["queries"][-100:]:
            words = query["text"].lower().split()
            keywords.extend([w for w in words if len(w) > 4])
        
        top_keywords = Counter(keywords).most_common(5)
        
        return {
            "total_users": len(self.data["total_users"]),
            "total_messages": self.data["total_messages"],
            "messages_today": self.data["messages_by_date"].get(today, 0),
            "top_keywords": top_keywords,
            "avg_messages_per_user": round(self.data["total_messages"] / max(len(self.data["total_users"]), 1), 1)
        }
