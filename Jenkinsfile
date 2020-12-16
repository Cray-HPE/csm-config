@Library('dst-shared@master') _
dockerBuildPipeline {
  repository = "cray"
  app = "csm-config"
  name = "csm-config"
  description = "Shasta CSM Helm Chart for import of CFS configuration content into VCS"
  product = "csm"
  enableSonar = false
  dockerfile = "Dockerfile"
  buildPrepScript = "runBuildPrep.sh"
}
