from celery import Celery
import asyncio
from praxis.conductor.conductor import Conductor

# Configure Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Initialize the Conductor
conductor = Conductor("path/to/config.ini")

# Example Celery task (you'll need to define this separately in a 'tasks.py' file)
@celery_app.task
def run_experiment_substep(experiment_name, substep_name, parameters):
    # Get the experiment instance from the Conductor (or a global dict)
    experiment = conductor.get_protocol(experiment_name) # Assuming you add a get_protocol method
    if experiment:
        # Execute the substep
        if hasattr(experiment, substep_name):
            substep_method = getattr(experiment, substep_name)
            if asyncio.iscoroutinefunction(substep_method):
                result = asyncio.run(substep_method(**parameters))  # If substep is async
            else:
                result = substep_method(**parameters)  # If substep is synchronous
            return result
        else:
            raise ValueError(f"Substep '{substep_name}' not found in experiment '{experiment_name}'")
    else:
        raise ValueError(f"Experiment '{experiment_name}' not found")

@celery_app.task
def run_plate_reader_task(experiment_name, plate_name, measurement_type, wells, estimated_duration, data_instance):
    # Similar to before, but you might need to adjust how you get data_instance
    # Perhaps you can pass it as an argument when creating the task or use a global
    # instance accessible to all tasks
    task = PlateReaderTask(experiment_name, plate_name, measurement_type, wells, estimated_duration, conductor.protocol_registry, data_instance)
    task.run_task()