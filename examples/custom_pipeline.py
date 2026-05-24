# Example: Custom Pipeline Configuration
from pipeline import Pipeline, Stage, PipelineConfig

def example_custom_pipeline():
    """Create a custom pipeline for a microservices project."""
    config = PipelineConfig(
        app_name="user-service",
        version="3.1.0",
        registry="gcr.io/my-project",
        namespace="production",
    )

    pipeline = Pipeline(config)

    # Add custom stages
    pipeline.add_stage(Stage("build", actions=["docker_build", "lint", "static_analysis"]))
    pipeline.add_stage(Stage("test", actions=["unit_tests", "integration_tests"]))
    pipeline.add_stage(Stage("deploy", actions=["tag_release", "docker_push", "k8s_apply"]))

    result = pipeline.run()
    print(f"Pipeline result: {result['status']}")

if __name__ == "__main__":
    example_custom_pipeline()
