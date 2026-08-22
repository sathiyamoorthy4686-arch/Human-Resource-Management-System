/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DayflowDashboard extends Component {
    static template = "dayflow_hr.Dashboard";

    setup() {
        this.rpc = useService("rpc");
        this.actionService = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            user: {},
            attendance: {
                is_checked_in: false,
                check_in_time: null,
                worked_hours: 0.0,
                status: "absent",
            },
            recent_leaves: [],
            salary: {},
            admin: {
                total_employees: 0,
                present_today: 0,
                absent_today: 0,
                on_leave_today: 0,
                pending_leaves: [],
                pending_count: 0,
                employees: [],
            },
            activities: [],
            chatOpen: false,
            chatInput: "",
            chatLoading: false,
            chatMessages: [{ role: "assistant", text: "Hi! Ask me a general HR question." }],
            liveTime: "",
            liveDate: "",
        });

        this.timer = null;

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.updateClock();
            this.timer = setInterval(() => {
                this.updateClock();
            }, 1000);
        });

        onWillUnmount(() => {
            if (this.timer) {
                clearInterval(this.timer);
            }
        });
    }

    updateClock() {
        const now = new Date();
        this.state.liveTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.state.liveDate = now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
    }

    async loadDashboardData() {
        try {
            const data = await this.rpc("/dayflow/dashboard_data", {});
            Object.assign(this.state.user, data.user || {});
            Object.assign(this.state.attendance, data.attendance || {});
            this.state.recent_leaves = data.recent_leaves || [];
            Object.assign(this.state.salary, data.salary || {});
            Object.assign(this.state.admin, data.admin || {});
            this.state.activities = data.activities || [];
        } catch (err) {
            console.error("Failed to fetch Dayflow dashboard data", err);
        }
    }

    async toggleAttendance() {
        try {
            const result = await this.rpc("/dayflow/attendance_toggle", {});
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
                return;
            }
            this.notification.add(result.message, { type: "success" });
            await this.loadDashboardData();
        } catch (err) {
            this.notification.add("Could not update attendance status.", { type: "danger" });
        }
    }

    async sendChatMessage() {
        const message = this.state.chatInput.trim();
        if (!message || this.state.chatLoading) {
            return;
        }
        this.state.chatInput = "";
        this.state.chatMessages.push({ role: "user", text: message });
        this.state.chatLoading = true;
        try {
            const result = await this.rpc("/dayflow/gemini_chat", { message });
            this.state.chatMessages.push({
                role: "assistant",
                text: result.answer || result.error || "I could not answer that right now.",
            });
        } catch (err) {
            this.state.chatMessages.push({ role: "assistant", text: "The AI assistant is temporarily unavailable." });
        } finally {
            this.state.chatLoading = false;
        }
    }

    async approveLeave(leaveId) {
        try {
            const comment = prompt("Add approval remarks (optional):") || "";
            const result = await this.rpc("/dayflow/approve_leave", {
                leave_id: leaveId,
                comment: comment,
            });
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
                return;
            }
            this.notification.add(result.message, { type: "success" });
            await this.loadDashboardData();
        } catch (err) {
            this.notification.add("Error approving leave.", { type: "danger" });
        }
    }

    async refuseLeave(leaveId) {
        try {
            const comment = prompt("Please specify reason for rejection:") || "";
            const result = await this.rpc("/dayflow/refuse_leave", {
                leave_id: leaveId,
                comment: comment,
            });
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
                return;
            }
            this.notification.add(result.message, { type: "warning" });
            await this.loadDashboardData();
        } catch (err) {
            this.notification.add("Error rejecting leave.", { type: "danger" });
        }
    }

    openAction(actionXmlId) {
        this.actionService.doAction(actionXmlId);
    }

    openEmployeeRecord(empId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "hr.employee",
            res_id: empId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("dayflow_hr.dashboard", DayflowDashboard);
