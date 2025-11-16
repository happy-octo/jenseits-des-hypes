
users=50

APP_NAME="sonnenschirm"

for ((i=1; i<=$users; i=i+1))
do
    USER="user$i"
    echo "Setting up $USER"

    oc new-project $USER-$APP_NAME
    oc adm policy add-role-to-user edit $USER -n $USER-$APP_NAME

    echo "Setup for $USER done"
done
