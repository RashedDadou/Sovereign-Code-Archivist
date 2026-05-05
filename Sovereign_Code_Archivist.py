# Sovereign_Code_Archivist.py

from collections import defaultdict
import time
import json
import os
from typing import Dict, List, Set, Optional

# ====================== 1. Persistence Manager ======================
class ArchivePersistence:
    def __init__(self, file_path: str = "sovereign_archive.json"):
        self.file_path = file_path

    def save(self, data: dict):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 تم حفظ الأرشيف → {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ خطأ حفظ: {e}")
            return False

    def load(self) -> dict:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ تحميل: {e}")
            return {}

# ====================== 2. Relationships Manager ======================
class RelationshipManager:
    def __init__(self):
        self.relationships = defaultdict(list)        # function → dependents
        self.reverse_relationships = defaultdict(list)  # function → dependencies

    def add_relationships(self, function_name: str, dependencies: List[str]):
        if not dependencies:
            return
        for dep in dependencies:
            if function_name not in self.relationships[dep]:
                self.relationships[dep].append(function_name)
            if dep not in self.reverse_relationships[function_name]:
                self.reverse_relationships[function_name].append(dep)

    def get_affected(self, function_name: str) -> List[str]:
        return self.relationships.get(function_name, [])

    def get_orphans(self) -> List[str]:
        orphans = []
        for func in self.relationships.keys() | self.reverse_relationships.keys():
            if not self.relationships[func] and not self.reverse_relationships[func]:
                orphans.append(func)
        return orphans

# ====================== 3. Code Analyzer ======================
class CodeAnalyzer:
    def __init__(self):
        self.split_keywords = ["process", "handle", "manage", "execute", "run", "perform", "convert", "transform", "main"]

    def analyze_function(self, function_name: str, code: str) -> dict:
        lines = len(code.splitlines())
        name_lower = function_name.lower()
        
        return {
            "size": lines,
            "name_complexity": len(function_name),
            "suggest_split": lines > 50 or any(k in name_lower for k in self.split_keywords),
            "reasons": self._get_split_reasons(function_name, lines)
        }

    def _get_split_reasons(self, name: str, size: int) -> List[str]:
        reasons = []
        if size > 50:
            reasons.append(f"كبيرة ({size} سطر)")
        if any(w in name.lower() for w in ["and", "or", "with", "plus", "&"]):
            reasons.append("تحتوي على عمليات متعددة")
        if len(name) > 35:
            reasons.append("اسم طويل")
        return reasons

# ====================== 4. Refinement Planner ======================
class RefinementPlanner:
    def __init__(self):
        self.refinement_history: Dict[str, int] = defaultdict(int)
        self.flagged: Set[str] = set()

    def flag_function(self, function_name: str):
        self.flagged.add(function_name)

    def record_refinement(self, function_name: str):
        self.refinement_history[function_name] += 1

    def get_plan(self, archive: dict, relationships: RelationshipManager) -> List[dict]:
        plan = []
        
        # أولوية 1: Flagged
        for func in sorted(self.flagged, key=lambda x: self.refinement_history[x], reverse=True):
            plan.append({"function": func, "priority": 1, "reason": "تحتاج توافق فوري"})

        # أولوية 2: كبيرة أو أساسية
        for func, data in sorted(archive.items(), key=lambda x: x[1].get("size", 0), reverse=True):
            if func not in self.flagged:
                plan.append({
                    "function": func,
                    "priority": 2,
                    "reason": f"دالة كبيرة ({data.get('size', 0)} سطر)"
                })
        return plan

# ====================== 5. Sovereign Code Archivist (الكلاس الرئيسي المنظم) ======================
class SovereignCodeArchivist:
    def __init__(self, persistence_path: str = "sovereign_archive.json"):
        self.persistence = ArchivePersistence(persistence_path)
        self.relationships = RelationshipManager()
        self.analyzer = CodeAnalyzer()
        self.planner = RefinementPlanner()
        
        self.archive: Dict[str, Dict] = {}
        self.versions: Dict[str, List[Dict]] = {}
        self.current_iteration = 0
        
        self.load()

    def archive_function(self, function_name: str, code: str, 
                        dependencies: List[str] = None, notes: str = ""):
        
        self.current_iteration += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        version = f"1.0.{len(self.versions.get(function_name, []))}"

        analysis = self.analyzer.analyze_function(function_name, code)

        entry = {
            "version": version,
            "code": code,
            "timestamp": timestamp,
            "dependencies": dependencies or [],
            "notes": notes,
            "size": analysis["size"],
            "status": "ACTIVE"
        }

        # حفظ
        if function_name not in self.versions:
            self.versions[function_name] = []
        self.versions[function_name].append(entry)
        self.archive[function_name] = entry

        self.relationships.add_relationships(function_name, dependencies)
        
        print(f"✅ أرشفة {function_name} v{version} ({analysis['size']} سطر)")
        self.coordinate_context()

    def notify_update(self, function_name: str, changes: str):
        if function_name not in self.archive:
            print("❌ الدالة غير موجودة")
            return

        self.planner.record_refinement(function_name)
        affected = self.relationships.get_affected(function_name)
        
        for func in affected:
            self.planner.flag_function(func)

        print(f"\n🔔 تحديث: {function_name} → {changes}")
        self.coordinate_context()

    def coordinate_context(self):
        print(f"\n{'='*70}")
        print(f"🔄 COORDINATE CONTEXT - الدورة #{self.current_iteration}")
        print(f"{'='*70}")

        plan = self.planner.get_plan(self.archive, self.relationships)
        orphans = self.relationships.get_orphans()

        # عرض التحليلات
        self._show_orphans(orphans)
        self._show_split_suggestions()
        self._show_plan(plan)
        self._show_health()

        self.save()

    def _show_orphans(self, orphans):
        print(f"\n🔍 الدوال اليتيمة: {'⚠️ ' + str(len(orphans)) if orphans else '✅ لا يوجد'}")

    def _show_split_suggestions(self):
        print("\n✂️  اقتراحات التقسيم:")
        suggested = False
        for name, data in self.archive.items():
            analysis = self.analyzer.analyze_function(name, data["code"])
            if analysis["suggest_split"]:
                print(f"   💡 {name} → {analysis['reasons']}")
                suggested = True
        if not suggested:
            print("   ✅ لا توجد اقتراحات تقسيم حالياً")

    def _show_plan(self, plan):
        print("\n📍 الخطة الحالية:")
        for i, item in enumerate(plan[:6], 1):
            print(f"   {i}. {item['function']} → {item['reason']}")

    def _show_health(self):
        health = 100 - (len(self.planner.flagged) * 12)
        print(f"\n📊 صحة المشروع: {max(0, health)}/100")

    def save(self):
        data = {
            "archive": self.archive,
            "versions": self.versions,
            "relationships": dict(self.relationships.relationships),
            "reverse_relationships": dict(self.relationships.reverse_relationships),
            "current_iteration": self.current_iteration
        }
        self.persistence.save(data)

    def load(self):
        data = self.persistence.load()
        if data:
            self.archive = data.get("archive", {})
            self.versions = data.get("versions", {})
            self.current_iteration = data.get("current_iteration", 0)
            print(f"✅ تم تحميل {len(self.archive)} دالة")