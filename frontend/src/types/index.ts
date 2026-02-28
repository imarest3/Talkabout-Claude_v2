export interface User {
    id: string;
    user_code: string;
    email: string | null;
    timezone: string;
    role: 'student' | 'teacher' | 'admin';
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
}

export interface AuthTokens {
    access: string;
    refresh: string;
}

export interface LoginResponse {
    access: string;
    refresh: string;
    user: User;
}

export interface Activity {
    id: string;
    code: string;
    title: string;
    description: string;
    max_participants_per_meeting: number;
    created_by: string;
    created_by_name?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    event_count?: number;
}

export interface Event {
    id: string;
    activity: string;
    activity_code: string;
    activity_title: string;
    start_datetime: string;
    end_datetime: string;
    waiting_time_minutes: number;
    status: 'scheduled' | 'in_waiting' | 'in_progress' | 'completed' | 'cancelled';
    enrolled_count?: number;
    attended_count?: number;
}

export interface Enrollment {
    id: string;
    student: string;
    student_name: string;
    event: string;
    enrolled_at: string;
    attended: boolean;
}

export interface Meeting {
    id: string;
    event: string;
    jitsi_room_name: string;
    jitsi_url: string;
    status: 'active' | 'completed';
    participants: string[]; // List of User IDs
}
