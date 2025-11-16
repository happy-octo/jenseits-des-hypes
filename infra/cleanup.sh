# --- VARS -----------------------------------------------------

NS=semantic-sonnenschirm


source install_cleanup_vars.sh


# --- Project -----------------------------------------------------
oc project $NS >/dev/null 2>&1
if [[ $? == 0 ]]; then
  echo "✅ Project $NS active"
else
  echo "💥 ERROR: Cannot switch to project $NS"
  exit
fi


# --- OpenShift Serverless Setup -----------------------------------------------------
if [[ "$CONF_KNATIVE" == true ]]; then
    echo "Delete OpenShift Serverless Setup..."
    oc delete -f knative-eventing.yaml
fi
