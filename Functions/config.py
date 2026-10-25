import tomllib
import tomli_w
import traceback
def get_config(file: str) -> dict:
    try: 
        if not file.endswith(".toml"):
            raise Exception("file isn't a toml file!")
        if not isinstance(file, str):
            raise TypeError(f"file must be str, got {type(file).__name__}")
        
        with open(file, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:

        return {"msg": f"config file {file} not found!", "error": True}
    except PermissionError:
        
        return {"msg": f"file access denied, check {file} permissions.", "error": True}
    except TypeError as e:
        return {"msg": str(e), "error": True} 
    except Exception:
        return {"msg": f"Exception: {traceback.format_exc()}", "error": True}

def set_config(file: str, section: str, name: str, value):
    if not file.endswith(".toml"):
        return {"msg": "file isn't a toml file!", "error": True}
    # get current config.
    current_config = get_config(file)
    
    # load new entry into the section -> name -> value
    current_config[section][name] = value
    try: 
        
        with open("config.toml", "wb") as f:
            tomli_w.dump(current_config, f)
        return {"msg": f"Functions/config.py: Successfully applied new config value for entry '{name}' in section '{section}' in '{file}' with '{value}'", "error": False}
    except FileNotFoundError as e:
        return {"msg": "File not found!", "error": True}
    except KeyError as e:
        return {"msg": f"Section '{e}' not found!", "error": True}
    except PermissionError as e:
        return {"msg": f"Permissions denied, check file permissions.", "error": True}
    except Exception as e:
        return {"msg": f"Exception: {traceback.format_exc()}", "error": True}
