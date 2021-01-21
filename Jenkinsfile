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

  githubPushRepo = "Cray-HPE/csm-config"
  /*
    By default all branches are pushed to GitHub

    Optionally, to limit which branches are pushed, add a githubPushBranches regex variable
    Examples:
    githubPushBranches =  /master/ # Only push the master branch

    In this case, we push bugfix, feature, hot fix, master, and release branches
  */
  githubPushBranches =  /(bugfix\/.*|feature\/.*|hotfix\/.*|master|release\/.*)/ 
}
