from flask import Blueprint, request, jsonify
from src.utils.scheduler import cpam_scheduler

bp_scheduler = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')

@bp_scheduler.route('/print', methods=['GET'])
def print_jobs():
    jobs = [f"id: {job.id}, name: {job}" for job in cpam_scheduler.get_jobs()]
    return jobs

@bp_scheduler.route('/pause', methods=['GET'])
def pause_job():
    cpam_scheduler.pause_job(job_id="cpam_ingestion")
    jobs = [f"id: {job.id}, name: {job}" for job in cpam_scheduler.get_jobs()]
    return jobs

@bp_scheduler.route('/resume', methods=['GET'])
def resume_job():
    cpam_scheduler.resume_job(job_id="cpam_ingestion")
    jobs = [f"id: {job.id}, name: {job}" for job in cpam_scheduler.get_jobs()]
    return jobs