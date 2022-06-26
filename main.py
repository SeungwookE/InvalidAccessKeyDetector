# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import asyncio
import datetime
import time
import collections
import json

# function to execute aws cli 'iam' command
async def getAwsIamData(require_data:str) -> list:
    command = "aws iam "
    command += require_data
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    return await process.communicate()


# function to get user list
async def getAwsUserList() -> str:
    output, errs = await getAwsIamData("list-users")
    if errs:
        print("Error occurred to get user list")
        return "error"

    return output.decode()


# function to get access key list
async def getAwsAccessKeys(userName) -> str:
    output, errs = await getAwsIamData("list-access-keys --user-name " + userName)
    if errs:
        print("Error occurred to get access key list:", errs)
        return "error"

    return output.decode()


# get access key list per user and arranging them in the dictionary
async def arrangeUserAccessKeyData(user_map, userName:str, current_time:float, valid_time:int):
    # request access key list assigned to {userName}
    keys = json.loads(await getAwsAccessKeys(userName))

    # iterate access keys and check if it is valid.
    for key in keys["AccessKeyMetadata"]:
        if await checkIsValid(key["CreateDate"], current_time, valid_time):
            user_map[key["UserName"]]["UserName"] = key["UserName"]
            user_map[key["UserName"]]["AccessKeyId"] = key["AccessKeyId"]
            user_map[key["UserName"]]["CreateDate"] = key["CreateDate"]


# check if create_time + valid_time is older than current_time
async def checkIsValid(created_time:str, current_time:float, valid_time:int) -> bool:
    date = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+00:00')
    created_at = time.mktime(date.timetuple())

    # print("diff: ", (current_time - (created_at + valid_time)) // 3600)
    if created_at + valid_time < current_time: # user is not valid
        return True
    else: # user is still valid
        return False


async def detectInvalidUserkey(valid_time:int):

    users = json.loads(await getAwsUserList())
    if users == "error":
        print("Error occurred to get User data")
        return

    # dictionary to save user/key data
    user_data = collections.defaultdict(dict)
    # current time to be base
    current_time = time.time()
    valid_time *= 3600

    tasks = []
    # get access keys per user and arrange them in 'user_data' dictionary
    for user in users["Users"]:
        tasks.append(arrangeUserAccessKeyData(user_data, user["UserName"], current_time, valid_time))
    # running the tasks asynchronously
    await asyncio.gather(*tasks)

    # write result(user_data) on the file
    with open("invalid_access_keys.txt", "w") as fd:
        fd.write(" - Get Invalid User List - At: " + datetime.datetime.fromtimestamp(current_time).strftime("%m/%d/%Y, %H:%M:%S") + "\n\n")
        for key, val in user_data.items():
            fd.write(" " + "{\n")
            for nkey, nval in val.items():
                fd.write(" \t" + nkey + ": " + nval + "\n")
            fd.write(" }\n")



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    limit = int(sys.argv[1])
    if not limit:
        print("please put validation time to filter access keys.")
    else:
        asyncio.run(detectInvalidUserkey(limit))

