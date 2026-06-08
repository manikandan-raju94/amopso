import optuna

storage = optuna.storages.RDBStorage(
    url=r"sqlite:///d:\Project Work\PSO\Static Optimization\AMPSO\optuna.db"
)

for s in storage.get_all_studies():
    print(s.study_name)