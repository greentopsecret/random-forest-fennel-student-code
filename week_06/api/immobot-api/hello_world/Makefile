include .env
export

env_report:
	aws lambda get-function-configuration --function-name ${FUNCTION_NAME}

env_update:
	aws lambda update-function-configuration --function-name ${FUNCTION_NAME} \
		--environment "Variables={`tr '\n' ',' < .env`}"