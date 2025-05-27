# Initial Guidance on Implementing Experiments

## Establishing Experimental Method

Set up method in script as a Experiment or ContinuousExperiment subclass and fill in the required
methods. Ideally, Operations will be used.

### Important considerations

PLR allows you to modify resources at will, allowing for bespoke object based state saving.
Take advantage of this as well as Experiment objects.
Have machines operations run independently. If you want different machines to work in a sequence,
have the execution depend on a state specified somewhere else (e.g. Experiment.step_four_completed).examples plate_reader.plate_loaded and liquid_handler.igrip.location is sufficient_distance(liquid_handler.igrip): plate read. This allows machines to be managed independently which can enable both scheduled and
