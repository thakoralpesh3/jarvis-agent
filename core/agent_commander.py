"""
Supreme Multi-Agent Commander & Boss Orchestrator for JARVIS.
Allows JARVIS to command, delegate tasks, supervise execution, and autonomously heal subordinate AI agents
(including the YouTube Shorts AI Agent, Project Incubator, and Workspace Agents).
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types

from config.settings import JarvisConfig, load_config
from core.youtube_commander import YouTubeShortsCommander
from core.autonomous_creator import AutonomousCreatorEngine
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


class AgentCommander:
    """Master orchestrator commanding and supervising all subordinate AI agents on the laptop."""

    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or load_config()
        self.client = genai.Client(api_key=self.config.api_key) if self.config.api_key else None
        self.youtube_commander = YouTubeShortsCommander()
        self.project_creator = AutonomousCreatorEngine(self.config)

    def list_subordinate_agents(self) -> List[Dict[str, Any]]:
        """List all subordinate agents registered under JARVIS's command."""
        yt_status = self.youtube_commander.get_schedule_status()
        
        agents = [
            {
                "name": "youtube_shorts_agent",
                "role": "Autonomous YouTube Shorts Creator & Publisher",
                "path": str(self.youtube_commander.youtube_dir),
                "status": yt_status.get("last_status", "standby"),
                "last_run": yt_status.get("last_run_date", "Never"),
                "total_completed": yt_status.get("total_completed_shorts", 0),
                "supervisor": "JARVIS Mark VII Core"
            },
            {
                "name": "autonomous_project_creator",
                "role": "End-to-End Software & Tool Creator",
                "path": str(Path.home() / "jarvis_projects"),
                "status": "ready",
                "last_run": "Active",
                "total_completed": len(list((Path.home() / "jarvis_projects").glob("*"))),
                "supervisor": "JARVIS Mark VII Core"
            }
        ]
        # Register Chamunda Automobile Enterprise Shop Sub-Agents (Under CEO Aradhya)
        try:
            sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
            from shop_subagents_engine import ChamundaShopSubagentsManager
            sub_mgr = ChamundaShopSubagentsManager()
            for sa in sub_mgr.list_subagents():
                agents.append({
                    "name": f"chamunda_{sa['agent_id']}",
                    "role": f"{sa['name']} ({sa['designated_head']})",
                    "path": "/home/alpesh/chamunda_re_enterprise",
                    "status": sa["status"],
                    "last_run": "Active",
                    "total_completed": len(sa.get("capabilities", [])),
                    "supervisor": "Aradhya • CEO (Chamunda Automobile)"
                })
        except Exception:
            pass

        return agents

    def command_agent(self, agent_name: str, task: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Issue a high-level command/order to a subordinate AI agent and oversee its execution.
        """
        agent_name_clean = agent_name.lower().replace("-", "_").replace(" ", "_")

        if "youtube" in agent_name_clean:
            niche = kwargs.get("niche")
            topic = kwargs.get("topic") or (task if task and not task.lower().startswith("run") else None)
            dry_run = kwargs.get("dry_run", False)
            return self.youtube_commander.run_and_supervise_pipeline(niche=niche, topic=topic, dry_run=dry_run)

        elif "project" in agent_name_clean or "creator" in agent_name_clean:
            proj_name = kwargs.get("project_name") or "Autonomous_Tool"
            res = self.project_creator.build_and_execute_project(proj_name, task)
            return {"success": True, "result": res}

        elif "chamunda" in agent_name_clean or any(k in agent_name_clean for k in ["bay", "parts", "receptionist", "social", "accounts"]):
            sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
            from shop_subagents_engine import ChamundaShopSubagentsManager
            sub_mgr = ChamundaShopSubagentsManager()
            # Clean name e.g. chamunda_bay_chief -> bay_chief
            raw_id = agent_name_clean.replace("chamunda_", "")
            res = sub_mgr.delegate_task(agent_id=raw_id, task_title=task[:60], task_description=task)
            return res

        else:
            return {"success": False, "error": f"Unknown subordinate agent: {agent_name}"}

    def diagnose_and_heal_subagent(self, agent_name: str, error_log: str) -> str:
        """
        Use Gemini reasoning to diagnose why a subordinate agent failed and apply a permanent fix.
        """
        agent_name_clean = agent_name.lower().replace("-", "_").replace(" ", "_")
        if "chamunda" in agent_name_clean or any(k in agent_name_clean for k in ["bay", "parts", "receptionist", "social", "accounts"]):
            sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
            from shop_subagents_engine import ChamundaShopSubagentsManager
            sub_mgr = ChamundaShopSubagentsManager()
            raw_id = agent_name_clean.replace("chamunda_", "")
            res = sub_mgr.diagnose_and_heal_incident(agent_id=raw_id, issue_description=error_log)
            if res.get("success"):
                return f"""### 🛡️ Chamunda Sub-Agent Autonomous Self-Healing Executed
**Sub-Agent:** {res['agent_name']} ({res['designated_head']})
**Incident ID:** `{res['incident_id']}` | **New Level:** Level {res['new_level']} ({res['total_xp']} XP)
**Issue Diagnosed:** {res['issue_reported']}
**Root Cause:** {res['root_cause_diagnosed']}
**Self-Healing Fix Applied:** {res['applied_solution']}
**New Capability Acquired:** `{res['new_skill_unlocked']}`
**ગુજરાતી અહેવાલ:** {res['solution_gu']}"""
            else:
                return f"Self-healing failed: {res.get('error')}"

        if not self.client:
            return "JARVIS Error: Gemini API client not configured."

        play_stark_sound("protocol")

        prompt = f"""You are JARVIS, Supreme AI Commander.
One of your subordinate agents ('{agent_name}') encountered an execution failure or error.
Your mission is to analyze the traceback, identify the exact defect, and provide:
1. Root Cause Analysis
2. Exact Self-Healing Fix / Code Patch
3. Resumption Directive to ensure the agent finishes 100% of its work.

Subordinate Agent Error Trace:
{error_log}

Respond with authoritative Stark Industries precision."""

        try:
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2)
            )
            return response.text or "Diagnosis completed without recommendations."
        except Exception as e:
            return f"Error diagnosing subagent: {str(e)}"

    def execute_written_directive(self, command_text: str, sender: str = "Alpesh Sir (Founder & Chairman)", priority: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a freeform written command from Alpesh Sir or CEO Aradhya.
        Routes to the appropriate subordinate agent (Chamunda Shop Subagents, YouTube Shorts, or Autonomous Projects).
        """
        cmd_lower = command_text.lower()
        if any(w in cmd_lower for w in ["lag", "lagging", "turbo", "boost", "speed up", "make laptop faster", "ઝડપી", "લેગ", "સ્પિડ", "clean ram", "free ram"]):
            res = self.execute_lag_cleanup_directive()
            return {
                "success": True,
                "target_agent": "system_optimizer",
                "directive": "System Performance Optimization & Lag Cleanup",
                "response_gu": res.get("message_gu", ""),
                "response_en": res.get("message_en", ""),
                "result": res
            }

        if any(w in cmd_lower for w in ["webar", "ar camera", "દિવ્ય દ્રષ્ટિ", "દિવ્ય-દ્રષ્ટિ", "torque overlay", "ટોર્ક માર્ગદર્શિકા"]):
            res = self.execute_webar_guide_directive()
            return {
                "success": True,
                "target_agent": "bay_chief",
                "directive": "WebAR Live Camera Engine Overlay",
                "response_gu": "સાહેબ, વેબAR કેમેરા ઓવરલે સક્રિય કરવામાં આવ્યું છે. J-Series હેડ બોલ્ટ્સ માટે 45 Nm ટોર્ક અને ૧ ➔ ૪ ક્રિસ-ક્રોસ સિક્વન્સ સ્ક્રીન પર દેખાય છે.",
                "response_en": "WebAR Camera Overlay active: Factory 45 Nm torque specs and 1->4 criss-cross tightening sequence projected onto engine.",
                "result": res
            }

        if any(w in cmd_lower for w in ["night locker", "emergency locker", "રાત્રિ સંરક્ષક", "રાત્રિ-સંરક્ષક", "નાઇટ લોકર", "હાઇવે લોકર"]):
            res = self.execute_emergency_locker_directive()
            return {
                "success": True,
                "target_agent": "customer_receptionist",
                "directive": "24/7 Highway Emergency Spares Locker",
                "response_gu": res.get("message_gu", "રાત્રિ કટોકટી લોકર આરક્ષણ સફળ."),
                "response_en": f"Emergency Locker Reserved: {res.get('reservation_id')} (Box: {res.get('box_id')})",
                "result": res
            }

        if any(w in cmd_lower for w in ["cloud shadow", "offline", "chhaya", "છાયા", "ઓફલાઇન", "ઓફલાઇન એક્સેસ"]):
            res = self.execute_cloud_shadow_directive(query_text=command_text, sender=sender)
            return {
                "success": True,
                "target_agent": "cloud_shadow_engine",
                "directive": "Project Chhaya Cloud Shadow Offline Access",
                "response_gu": res.get("response_gu", "ક્લાઉડ શેડો સ્ટેન્ડબાય સક્રિય છે."),
                "response_en": res.get("response_en", "Cloud Shadow Standby Active."),
                "result": res
            }

        if any(w in cmd_lower for w in ["kalpavriksha", "virtual growth", "synthetic simulation", "simulate", "કલ્પવૃક્ષ", "તાલીમ", "શીખો", "વર્ચ્યુઅલ ગ્રોથ"]):
            res = self.execute_kalpavriksha_directive(action="simulate")
            return {
                "success": True,
                "target_agent": "kalpavriksha_growth_engine",
                "directive": "Project Kalpavriksha Autonomous Virtual Growth & Simulation",
                "response_gu": res.get("solution_gu", "કલ્પવૃક્ષ સ્વાયત્ત સિમ્યુલેશન પૂર્ણ."),
                "response_en": res.get("message", "Kalpavriksha synthetic practice simulation complete."),
                "result": res
            }

        if any(w in cmd_lower for w in ["youtube", "shorts"]) and not any(w in cmd_lower for w in ["chamunda", "workshop", "re", "bullet", "classic", "royal", "kabir", "કબીર"]):
            res = self.youtube_commander.run_and_supervise_pipeline(topic=command_text, dry_run=False)
            return {"success": True, "agent": "youtube_shorts_agent", "result": res}

        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from shop_subagents_engine import ChamundaShopSubagentsManager
        sub_mgr = ChamundaShopSubagentsManager()
        return sub_mgr.execute_written_command(command_text=command_text, sender=sender, priority=priority)

    def execute_bay_voice_directive(self, spoken_text: str, mechanic_name: str = "Master Tech Ramesh", bay_id: str = "Bay 1 (J-Series Platform)") -> Dict[str, Any]:
        """
        Process hands-free spoken workshop voice command from bay mechanics.
        Coordinates bay job card, parts inventory, accounts billing, and customer WhatsApp alert.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from bay_voice_engine import get_bay_voice_engine
        engine = get_bay_voice_engine()
        return engine.process_voice_action(spoken_text=spoken_text, mechanic_name=mechanic_name, bay_id=bay_id)

    def execute_b2b_wholesale_directive(self, garage_id: str, items: List[Dict[str, Any]], payment_mode: str = "Credit") -> Dict[str, Any]:
        """
        Process B2B wholesale parts order for North Gujarat partner garages.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from b2b_wholesale_engine import get_b2b_wholesale_manager
        mgr = get_b2b_wholesale_manager()
        return mgr.create_order(garage_id=garage_id, items=items, payment_mode=payment_mode)

    def execute_obd_diagnostic_directive(self, bike_model: str = "Classic 350 (Reborn)", registration_no: str = "GJ-02-BQ-1234", simulate_dtc: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute live OBD-II diagnostic scan, read telemetry, and decode DTC fault codes.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from obd_diagnostics_engine import get_obd_diagnostics_engine
        engine = get_obd_diagnostics_engine()
        return engine.run_obd_scan(bike_model=bike_model, registration_no=registration_no, simulate_dtc=simulate_dtc)

    def execute_kiosk_checkin_directive(self, registration_no: str, customer_name: str, phone: str, bike_model: str, selected_issues: List[str]) -> Dict[str, Any]:
        """
        Process fast-track rider lounge self-check-in and generate queue token.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from smart_kiosk_engine import get_smart_kiosk_engine
        engine = get_smart_kiosk_engine()
        return engine.process_checkin(
            registration_no=registration_no,
            customer_name=customer_name,
            phone=phone,
            bike_model=bike_model,
            selected_issues=selected_issues
        )

    def execute_schematic_lookup_directive(self, assembly_id: str = "ASM-J350-HEAD") -> Dict[str, Any]:
        """
        Look up 3D exploded assembly, component list, and factory torque specs.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from schematics_3d_engine import get_schematics_3d_engine
        engine = get_schematics_3d_engine()
        assembly = engine.get_assembly_by_id(assembly_id)
        if not assembly:
            assemblies = engine.get_assemblies()
            return {"found": False, "message": f"Assembly {assembly_id} not found.", "available": [a["assembly_id"] for a in assemblies]}
        return {"found": True, "assembly": assembly}

    def execute_borescope_directive(
        self,
        bike_model: str = "Classic 350 (Reborn)",
        registration_no: str = "GJ-02-BQ-1234",
        odometer_km: int = 15000,
        scenario: str = "heavy_carbon_crust"
    ) -> Dict[str, Any]:
        """
        Execute non-invasive AI borescope endoscopic inspection of cylinder bore and combustion chamber.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from borescope_inspection_engine import get_borescope_engine
        engine = get_borescope_engine()
        return engine.inspect_combustion_chamber(
            bike_model=bike_model,
            registration_no=registration_no,
            odometer_km=odometer_km,
            scenario=scenario
        )

    def execute_branch_transfer_directive(
        self,
        from_branch: str,
        to_branch: str,
        part_number: str,
        quantity: int = 1,
        requested_by: str = "Branch Lead",
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Dispatch intra-branch stock transfer across North Gujarat Chamunda branches.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from multibranch_hub_engine import get_multibranch_engine
        engine = get_multibranch_engine()
        return engine.transfer_stock(
            from_branch=from_branch,
            to_branch=to_branch,
            part_number=part_number,
            quantity=quantity,
            requested_by=requested_by,
            notes=notes
        )

    def execute_lag_cleanup_directive(self, aggressive: bool = False, close_stale_processes: bool = True) -> Dict[str, Any]:
        """
        Execute system optimization, garbage collection, and stale process termination to resolve laptop lag.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from system_optimizer import get_system_optimizer
        optimizer = get_system_optimizer()
        return optimizer.optimize_laptop_performance(aggressive=aggressive, close_stale_processes=close_stale_processes)

    def execute_webar_guide_directive(self, assembly_id: str = "AR-J350-HEAD") -> Dict[str, Any]:
        """
        Retrieve WebAR live camera overlay coordinates, torque limits, and tightening sequence.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from webar_engine_guide import get_webar_engine
        engine = get_webar_engine()
        return engine.calculate_ar_camera_view(assembly_id=assembly_id)

    def execute_emergency_locker_directive(
        self,
        box_id: str = "BOX-01",
        customer_name: str = "Touring Rider",
        phone: str = "+91 98250 12345",
        vehicle_reg: str = "GJ-02-BQ-1234"
    ) -> Dict[str, Any]:
        """
        Reserve an emergency night spares locker compartment and generate dynamic UPI QR + unlock OTP.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from night_locker_engine import get_night_locker_manager
        mgr = get_night_locker_manager()
        return mgr.reserve_compartment(
            box_id=box_id,
            customer_name=customer_name,
            phone=phone,
            vehicle_reg=vehicle_reg
        )

    def execute_cloud_shadow_directive(
        self,
        action: str = "query",
        query_text: str = "Check workshop status",
        sender: str = "Alpesh Sir (Founder & Chairman)",
        phone: str = "+91 78747 19139"
    ) -> Dict[str, Any]:
        """
        Execute Cloud Shadow offline access operations (query, snapshot, sync).
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from cloud_shadow_engine import get_cloud_shadow_manager
        mgr = get_cloud_shadow_manager()
        if action == "snapshot":
            return mgr.generate_state_snapshot()
        elif action == "reconcile":
            return mgr.reconcile_sync()
        elif action == "status":
            return mgr.get_shadow_telemetry()
        else:
            return mgr.process_remote_offline_query(query_text=query_text, sender=sender, phone=phone)

    def execute_kalpavriksha_directive(
        self,
        action: str = "simulate",
        spec_payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Project Kalpavriksha virtual growth simulation, knowledge ingestion, or telemetry audit.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from kalpavriksha_growth_engine import get_kalpavriksha_engine
        engine = get_kalpavriksha_engine()
        if action == "status":
            return engine.get_growth_telemetry()
        elif action == "ingest" and spec_payload:
            return engine.ingest_technical_manual_spec(
                engine_family=spec_payload.get("engine_family", "J-Series 350"),
                category=spec_payload.get("category", "General"),
                target_components=spec_payload.get("target_components", "Engine"),
                torque_sequence=spec_payload.get("torque_sequence", "Factory Standard"),
                clearances=spec_payload.get("clearances", "Standard"),
                ramesh_secret=spec_payload.get("ramesh_secret", "Verify before final torque")
            )
        else:
            return engine.run_synthetic_diagnostic_simulation()

    def execute_dms_directive(
        self,
        action: str = "overview",
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute official Royal Enfield Dealer Management System (RE-DMS Suite) directives:
        - overview: Telemetry, active invoices, GSTIN, accounts summary, campaigns, and fleet status.
        - create_invoice: Split GST invoice (Labor SAC 998729 & Spares HSN 8714) with UPI QR and Gate Pass.
        - file_warranty_claim: OEM Free Service Coupon (FSC) or warranty claim filing.
        - create_campaign: WhatsApp broadcast / seasonal campaign creation.
        - dispatch_service_reminders: Automated 30/60/90-day predictive WhatsApp service notifications.
        - get_daybook: Double-entry financial daybook and ledger.
        - get_leads: Pipeline of test-ride and new bike booking leads.
        """
        sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
        from dms_enterprise_suite_engine import get_dms_suite_engine
        dms = get_dms_suite_engine()
        params = params or {}

        if action == "overview":
            return {"success": True, "overview": dms.get_dms_overview_telemetry()}
        elif action == "create_invoice":
            return dms.create_split_gst_invoice(**params)
        elif action == "file_warranty_claim":
            return dms.file_oem_warranty_claim(**params)
        elif action == "create_campaign":
            return dms.create_marketing_campaign(**params)
        elif action == "dispatch_service_reminders":
            return dms.dispatch_service_reminders(**params)
        elif action == "get_daybook":
            return dms.get_daybook_summary()
        elif action == "get_leads":
            return {"success": True, "leads": dms.get_leads_pipeline()}
        elif action == "create_booking":
            return dms.create_vehicle_booking(**params)
        elif action == "generate_pdi":
            return dms.generate_pdi_inspection(**params)
        elif action == "issue_ride_sure":
            return dms.issue_ride_sure_warranty(**params)
        elif action == "create_insurance_claim":
            return dms.create_insurance_claim_estimate(**params)
        elif action == "record_psf":
            return dms.record_post_service_feedback(**params)
        elif action == "csat_telemetry":
            return {"success": True, "csat": dms.get_csat_and_qc_telemetry()}
        elif action == "showroom_telemetry":
            return {"success": True, "showroom": dms.get_showroom_sales_telemetry()}
        else:
            return {"success": False, "error": f"Unknown DMS action: {action}"}


ChamundaAgentCommander = AgentCommander

