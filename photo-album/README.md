# Introduction

The purpose of this APP is to demonstrate, what it takes for a developer to interact with OpenShift Container Storage Object Bucket Claim feature and consume Object Storage as a persistent layer.

# Duration

This demo takes about 3min to run.

# Run the demo:

The demo script will make sure the namespace is in place and clean up existing instances of the app before building the resources to re-deploy the app.

``./demo.sh``

# Components

`BuildConfig`
: Image configuration from source

`ImageStream`
: Reference to the container image

`DeploymentConfig`
: Application deployment configuration

`ObjectBucketClaim`
: Photo storage

`Service`
: Web service

`Route`
: `photo-album.{{domain}}`

# Deployment

<pre>
$ ./demo.sh
[ OK    ] Using apps.ocp.webwim.com as our base domain
[ OK    ] oc apply -f /srv/redhat/demo/namespace.yaml
namespace/demo unchanged

Object Bucket Demo

 * Cleanup existing environment

Press any key to continue... 

[ OK    ] oc delete --ignore-not-found=1 -f app.yaml
objectbucketclaim.objectbucket.io "photo-album" deleted
deploymentconfig.apps.openshift.io "photo-album" deleted
service "photo-album" deleted
route.route.openshift.io "photo-album" deleted

[ OK    ] oc delete --ignore-not-found=1 bc photo-album -n demo
buildconfig.build.openshift.io "photo-album" deleted

 * Import dependencies and create build config

Press any key to continue... 

[ OK    ] oc import-image ubi8/python-38 --from=registry.redhat.io/ubi8/python-38 --confirm -n demo
ubi8/python-38 imported

 * Deploy application

[ OK    ] oc create -f app.yaml
objectbucketclaim.objectbucket.io/photo-album created
deploymentconfig.apps.openshift.io/photo-album created
service/photo-album created
route.route.openshift.io/photo-album created

 * Build the application image

[ OK    ] oc new-build --binary --strategy=docker --name photo-album -n demo
photo-album built

[ OK    ] oc start-build photo-album --from-dir . -F -n demo
photo-album setup
/srv/redhat/demo/photo-album
</pre>

This should create an OBC and other stuff needed for the app itself like POD,SVC,ROUTE. Together with OBC, you will also get new secrets and config maps created. The important resources could be listed as

- `oc get obc,secret,configmap,deployment,pod,svc,route`

At this point your app is ready to be accessed externally. Grab the URL and browse it:

- http://photo-album.{{domain}}/

- The landing page allows image to be selected and uploaded.

![](documentation/screenshots/Demo%20App%20-%20Start.png)

- Once uploaded images are listed an can be selected to view larger.

![](documentation/screenshots/Demo%20App%20-%20With%20Image.png)

# Documentation / Screenshots

See the [`documentation/screenshots`](documentation/screenshots) folder.

# Credits

This demo was inspired and derived from the following applications:

* [Red Hat Storage `photo-album`][photo-album-ocs] demo app.
* [karan singh's `photo album`][photo-album-app] app.

[photo-album-app]: https://github.com/ksingh7/openshift-photo-album-app
[photo-album-ocs]: https://github.com/red-hat-storage/demo-apps/blob/main/photo-album
